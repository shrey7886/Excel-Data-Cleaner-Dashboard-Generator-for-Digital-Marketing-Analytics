import pandas as pd
import xlsxwriter
from typing import Dict, List
import logging
from datetime import datetime
import numpy as np

def create_dashboard(df: pd.DataFrame, output_file: str) -> None:
    """
    Create a Targetorate-specific Excel dashboard with comprehensive marketing analytics.
    """
    try:
        # Ensure all string columns are properly formatted
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str)

        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            # Cover Sheet
            cover_df = pd.DataFrame({
                'A': [
                    'Targetorate Marketing Analytics Dashboard',
                    '',
                    f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                    '',
                    'This dashboard provides comprehensive marketing analytics with KPIs, trends, and campaign performance insights.',
                    'Includes specialized metrics for digital marketing, consulting, and GTM strategies across India and US markets.'
                ]
            })
            cover_df.to_excel(writer, sheet_name='Cover', index=False, header=False)
            cover_ws = writer.sheets['Cover']
            cover_ws.set_column('A:A', 80)
            title_format = writer.book.add_format({'bold': True, 'font_size': 20, 'align': 'center'})
            cover_ws.write('A1', 'Targetorate Marketing Analytics', title_format)

            # Write all data to 'Data' sheet with enhanced formatting
            df.to_excel(writer, sheet_name='Data', index=False)
            data_ws = writer.sheets['Data']
            
            # Add number formatting to Data sheet
            number_format = writer.book.add_format({'num_format': '#,##0.00'})
            currency_format = writer.book.add_format({'num_format': '$#,##0.00'})
            percent_format = writer.book.add_format({'num_format': '0.00%'})
            
            # Apply formatting to columns
            for col_num, value in enumerate(df.columns.values):
                if 'Cost' in value or 'Revenue' in value:
                    data_ws.set_column(col_num, col_num, 15, currency_format)
                elif 'CTR' in value or 'ROAS' in value:
                    data_ws.set_column(col_num, col_num, 12, percent_format)
                else:
                    data_ws.set_column(col_num, col_num, 15, number_format)

            # Create summary sheet with enhanced metrics
            summary_df = pd.DataFrame({
                'Metric': [
                    # Basic Metrics
                    'Total Impressions', 'Total Clicks', 'Total Cost', 
                    'Total Conversions', 'Total Revenue', 'Average CTR',
                    'Average CPC', 'Average ROAS', 'Average CPA',
                    
                    # Targetorate-Specific Metrics
                    'Cost per Lead (CPL)',
                    'Engagement Rate',
                    'Organic vs Paid Conversion Ratio',
                    'India Market ROAS',
                    'US Market ROAS',
                    'Google Ads Spend',
                    'Meta Ads Spend',
                    'LinkedIn Ads Spend',
                    
                    # Campaign Performance
                    'Best Campaign (ROAS)',
                    'Worst Campaign (ROAS)',
                    'Best Campaign (CTR)',
                    'Worst Campaign (CTR)',
                    'Best Campaign (CPC)',
                    'Worst Campaign (CPC)'
                ],
                'Value': [
                    # Basic Metrics
                    df['Impressions'].sum(),
                    df['Clicks'].sum(),
                    df['Cost'].sum(),
                    df['Conversions'].sum(),
                    df['Revenue'].sum(),
                    df['CTR'].mean(),
                    df['CPC'].mean(),
                    df['ROAS'].mean(),
                    df['CPA'].mean(),
                    
                    # Targetorate-Specific Metrics
                    df['Cost'].sum() / df['Conversions'].sum() if df['Conversions'].sum() > 0 else 0,
                    (df['Clicks'].sum() + df['Conversions'].sum()) / df['Impressions'].sum() if df['Impressions'].sum() > 0 else 0,
                    df[df['Campaign Name'].str.contains('Organic', case=False, na=False)]['Conversions'].sum() / 
                    df[df['Campaign Name'].str.contains('Paid', case=False, na=False)]['Conversions'].sum() if df[df['Campaign Name'].str.contains('Paid', case=False, na=False)]['Conversions'].sum() > 0 else 0,
                    df[df['Campaign Name'].str.contains('India', case=False, na=False)]['ROAS'].mean(),
                    df[df['Campaign Name'].str.contains('US', case=False, na=False)]['ROAS'].mean(),
                    df[df['Campaign Name'].str.contains('Google', case=False, na=False)]['Cost'].sum(),
                    df[df['Campaign Name'].str.contains('Meta', case=False, na=False)]['Cost'].sum(),
                    df[df['Campaign Name'].str.contains('LinkedIn', case=False, na=False)]['Cost'].sum(),
                    
                    # Campaign Performance
                    df.groupby('Campaign Name')['ROAS'].mean().idxmax() if not df.empty else 'N/A',
                    df.groupby('Campaign Name')['ROAS'].mean().idxmin() if not df.empty else 'N/A',
                    df.groupby('Campaign Name')['CTR'].mean().idxmax() if not df.empty else 'N/A',
                    df.groupby('Campaign Name')['CTR'].mean().idxmin() if not df.empty else 'N/A',
                    df.groupby('Campaign Name')['CPC'].mean().idxmin() if not df.empty else 'N/A',
                    df.groupby('Campaign Name')['CPC'].mean().idxmax() if not df.empty else 'N/A'
                ]
            })
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            summary_ws = writer.sheets['Summary']
            summary_ws.set_column('A:A', 35)
            summary_ws.set_column('B:B', 30)
            header_format = writer.book.add_format({'bold': True, 'bg_color': '#D9E1F2'})
            summary_ws.write('A1', 'Metric', header_format)
            summary_ws.write('B1', 'Value', header_format)

            # Get workbook object
            workbook = writer.book

            # --- Charts Sheet ---
            charts_ws = workbook.add_worksheet('Charts')
            chart_row = 1

            # 📈 Time Series Analysis
            charts_ws.write('A1', '📈 Time Series Analysis', workbook.add_format({'bold': True, 'font_size': 14}))
            chart_row = 2
            if not df.empty and 'Date' in df.columns and 'CTR' in df.columns:
                chart_row = insert_time_series_chart(workbook, charts_ws, df, 'CTR', 'Data', chart_row)
            if not df.empty and 'Date' in df.columns and 'CPC' in df.columns:
                chart_row = insert_time_series_chart(workbook, charts_ws, df, 'CPC', 'Data', chart_row)
            if not df.empty and 'Date' in df.columns and 'Revenue' in df.columns and 'Cost' in df.columns:
                chart_row = insert_revenue_cost_chart(workbook, charts_ws, df, 'Data', chart_row)
            if not df.empty and 'Date' in df.columns and 'ROAS' in df.columns:
                chart_row = insert_monthly_roas_chart(workbook, charts_ws, df, chart_row)

            # 📊 Campaign Performance
            charts_ws.write(f'A{chart_row}', '📊 Campaign Performance', workbook.add_format({'bold': True, 'font_size': 14}))
            chart_row += 1
            if not df.empty and 'Campaign Name' in df.columns and 'Conversions' in df.columns:
                chart_row = insert_bar_chart(workbook, charts_ws, df, 'Campaign Name', 'Conversions', 'Data', chart_row)
            if not df.empty and 'Campaign Name' in df.columns and 'Cost' in df.columns:
                chart_row = insert_bar_chart(workbook, charts_ws, df, 'Campaign Name', 'Cost', 'Data', chart_row)
            if not df.empty and 'Campaign Name' in df.columns and 'ROAS' in df.columns:
                chart_row = insert_bar_chart(workbook, charts_ws, df, 'Campaign Name', 'ROAS', 'Data', chart_row)

            # 🧮 Campaign Analysis
            charts_ws.write(f'A{chart_row}', '🧮 Campaign Analysis', workbook.add_format({'bold': True, 'font_size': 14}))
            chart_row += 1
            if not df.empty and 'Campaign Name' in df.columns and 'Cost' in df.columns:
                chart_row = insert_pie_chart(workbook, charts_ws, df, 'Campaign Name', 'Cost', chart_row)
            if not df.empty and 'Impressions' in df.columns and 'Clicks' in df.columns and 'Conversions' in df.columns:
                chart_row = insert_funnel_chart(workbook, charts_ws, df, chart_row)
            if not df.empty and 'Campaign Name' in df.columns and 'ROAS' in df.columns:
                chart_row = insert_geo_performance_chart(workbook, charts_ws, df, chart_row)

            # 🧠 Smart Analysis
            charts_ws.write(f'A{chart_row}', '🧠 Smart Analysis', workbook.add_format({'bold': True, 'font_size': 14}))
            chart_row += 1
            if not df.empty and 'Campaign Name' in df.columns and 'ROAS' in df.columns:
                chart_row = insert_top_performers_chart(workbook, charts_ws, df, 'ROAS', chart_row)
            if not df.empty and 'Campaign Name' in df.columns and 'CTR' in df.columns:
                chart_row = insert_top_performers_chart(workbook, charts_ws, df, 'CTR', chart_row)
            if not df.empty and 'Campaign Name' in df.columns and 'ROAS' in df.columns and 'CTR' in df.columns and 'CPC' in df.columns:
                chart_row = insert_worst_performers_chart(workbook, charts_ws, df, chart_row)

            # 📝 Smart Recommendations
            recommendations_ws = workbook.add_worksheet('Smart Recommendations')
            recommendations_ws.set_column('A:A', 100)
            recommendations_ws.write('A1', 'Smart Recommendations', workbook.add_format({'bold': True, 'font_size': 14}))
            
            # Generate recommendations
            recommendations = generate_recommendations(df)
            for idx, rec in enumerate(recommendations, start=2):
                recommendations_ws.write(f'A{idx}', rec)

            # Conditional Formatting in Data sheet
            highlight_format = workbook.add_format({'bg_color': '#C6EFCE'})  # Green for good
            warning_format = workbook.add_format({'bg_color': '#FFC7CE'})    # Red for bad

            # Highlight best performers
            if not df.empty and 'Campaign Name' in df.columns:
                best_roas = df.groupby('Campaign Name')['ROAS'].mean().nlargest(3)
                best_ctr = df.groupby('Campaign Name')['CTR'].mean().nlargest(3)
                best_cpc = df.groupby('Campaign Name')['CPC'].mean().nsmallest(3)

                for idx, row in df.iterrows():
                    if row['Campaign Name'] in best_roas.index:
                        data_ws.write(idx + 1, df.columns.get_loc('ROAS'), row['ROAS'], highlight_format)
                    if row['Campaign Name'] in best_ctr.index:
                        data_ws.write(idx + 1, df.columns.get_loc('CTR'), row['CTR'], highlight_format)
                    if row['Campaign Name'] in best_cpc.index:
                        data_ws.write(idx + 1, df.columns.get_loc('CPC'), row['CPC'], highlight_format)

    except Exception as e:
        logging.error(f"Error creating dashboard: {str(e)}")
        raise

def insert_time_series_chart(workbook, charts_ws, df, metric, data_sheet, chart_row):
    chart = workbook.add_chart({'type': 'line'})
    col_idx = df.columns.get_loc(metric)
    chart.add_series({
        'name': metric,
        'categories': [data_sheet, 1, 0, len(df), 0],
        'values': [data_sheet, 1, col_idx, len(df), col_idx],
        'line': {'width': 2.5}
    })
    chart.set_title({'name': f'{metric} Over Time'})
    chart.set_x_axis({'name': 'Date'})
    chart.set_y_axis({'name': metric})
    charts_ws.insert_chart(chart_row, 1, chart)
    return chart_row + 18

def insert_revenue_cost_chart(workbook, charts_ws, df, data_sheet, chart_row):
    chart = workbook.add_chart({'type': 'line'})
    revenue_idx = df.columns.get_loc('Revenue')
    cost_idx = df.columns.get_loc('Cost')
    
    chart.add_series({
        'name': 'Revenue',
        'categories': [data_sheet, 1, 0, len(df), 0],
        'values': [data_sheet, 1, revenue_idx, len(df), revenue_idx],
        'line': {'width': 2.5, 'color': '#00B050'}
    })
    
    chart.add_series({
        'name': 'Cost',
        'categories': [data_sheet, 1, 0, len(df), 0],
        'values': [data_sheet, 1, cost_idx, len(df), cost_idx],
        'line': {'width': 2.5, 'color': '#FF0000'}
    })
    
    chart.set_title({'name': 'Revenue vs Cost Over Time'})
    chart.set_x_axis({'name': 'Date'})
    chart.set_y_axis({'name': 'Amount ($)'})
    charts_ws.insert_chart(chart_row, 1, chart)
    return chart_row + 18

def insert_bar_chart(workbook, charts_ws, df, category_col, value_col, data_sheet, chart_row):
    chart = workbook.add_chart({'type': 'column'})
    cat_idx = df.columns.get_loc(category_col)
    val_idx = df.columns.get_loc(value_col)
    
    chart.add_series({
        'name': value_col,
        'categories': [data_sheet, 1, cat_idx, len(df), cat_idx],
        'values': [data_sheet, 1, val_idx, len(df), val_idx],
    })
    
    chart.set_title({'name': f'{value_col} by {category_col}'})
    chart.set_x_axis({'name': category_col})
    chart.set_y_axis({'name': value_col})
    charts_ws.insert_chart(chart_row, 1, chart)
    return chart_row + 18

def insert_pie_chart(workbook, charts_ws, df, category_col, value_col, chart_row):
    pie_data = df.groupby(category_col)[value_col].sum().reset_index()
    pie_sheet = workbook.add_worksheet('PieData')
    pie_sheet.write(0, 0, category_col)
    pie_sheet.write(0, 1, value_col)
    for idx, row in pie_data.iterrows():
        pie_sheet.write(idx + 1, 0, row[category_col])
        pie_sheet.write(idx + 1, 1, row[value_col])
    
    chart = workbook.add_chart({'type': 'pie'})
    chart.add_series({
        'name': f'{value_col} by {category_col}',
        'categories': ['PieData', 1, 0, len(pie_data), 0],
        'values': ['PieData', 1, 1, len(pie_data), 1],
    })
    chart.set_title({'name': f'{value_col} Distribution by {category_col}'})
    charts_ws.insert_chart(chart_row, 1, chart)
    return chart_row + 18

def insert_top_performers_chart(workbook, charts_ws, df, metric, chart_row):
    # Get top 5 performers
    top_performers = df.groupby('Campaign Name')[metric].mean().nlargest(5).reset_index()
    
    # Create data sheet for chart
    sheet_name = f'Top{metric}Data'
    data_sheet = workbook.add_worksheet(sheet_name)
    data_sheet.write(0, 0, 'Campaign Name')
    data_sheet.write(0, 1, metric)
    
    for idx, row in top_performers.iterrows():
        data_sheet.write(idx + 1, 0, row['Campaign Name'])
        data_sheet.write(idx + 1, 1, row[metric])
    
    chart = workbook.add_chart({'type': 'column'})
    chart.add_series({
        'name': f'Top 5 {metric}',
        'categories': [sheet_name, 1, 0, len(top_performers), 0],
        'values': [sheet_name, 1, 1, len(top_performers), 1],
    })
    chart.set_title({'name': f'Top 5 Campaigns by {metric}'})
    charts_ws.insert_chart(chart_row, 1, chart)
    return chart_row + 18

def insert_worst_performers_chart(workbook, charts_ws, df, chart_row):
    # Calculate efficiency score (ROAS * CTR / CPC)
    campaign_metrics = df.groupby('Campaign Name').agg({
        'ROAS': 'mean',
        'CTR': 'mean',
        'CPC': 'mean',
        'Cost': 'sum',
        'Conversions': 'sum'
    })
    campaign_metrics['Efficiency Score'] = (campaign_metrics['ROAS'] * campaign_metrics['CTR']) / campaign_metrics['CPC']
    
    # Get worst 5 performers
    worst_performers = campaign_metrics.nsmallest(5, 'Efficiency Score').reset_index()
    
    # Create data sheet for chart
    sheet_name = 'WorstPerformersData'
    data_sheet = workbook.add_worksheet(sheet_name)
    data_sheet.write(0, 0, 'Campaign Name')
    data_sheet.write(0, 1, 'Efficiency Score')
    
    for idx, row in worst_performers.iterrows():
        data_sheet.write(idx + 1, 0, row['Campaign Name'])
        data_sheet.write(idx + 1, 1, row['Efficiency Score'])
    
    chart = workbook.add_chart({'type': 'column'})
    chart.add_series({
        'name': 'Worst 5 Campaigns',
        'categories': [sheet_name, 1, 0, len(worst_performers), 0],
        'values': [sheet_name, 1, 1, len(worst_performers), 1],
    })
    chart.set_title({'name': 'Worst 5 Campaigns by Efficiency Score'})
    charts_ws.insert_chart(chart_row, 1, chart)
    return chart_row + 18

def insert_monthly_roas_chart(workbook, charts_ws, df, chart_row):
    # Aggregate ROAS by month
    df['Month'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m')
    monthly_roas = df.groupby('Month')['ROAS'].mean().reset_index()
    
    # Create data sheet for chart
    sheet_name = 'MonthlyROASData'
    data_sheet = workbook.add_worksheet(sheet_name)
    data_sheet.write(0, 0, 'Month')
    data_sheet.write(0, 1, 'ROAS')
    
    for idx, row in monthly_roas.iterrows():
        data_sheet.write(idx + 1, 0, row['Month'])
        data_sheet.write(idx + 1, 1, row['ROAS'])
    
    chart = workbook.add_chart({'type': 'line'})
    chart.add_series({
        'name': 'Monthly ROAS',
        'categories': [sheet_name, 1, 0, len(monthly_roas), 0],
        'values': [sheet_name, 1, 1, len(monthly_roas), 1],
        'line': {'width': 2.5, 'color': '#0070C0'}
    })
    chart.set_title({'name': 'Monthly ROAS Trend'})
    chart.set_x_axis({'name': 'Month'})
    chart.set_y_axis({'name': 'ROAS'})
    charts_ws.insert_chart(chart_row, 1, chart)
    return chart_row + 18

def insert_funnel_chart(workbook, charts_ws, df, chart_row):
    # Calculate funnel metrics
    funnel_data = pd.DataFrame({
        'Stage': ['Impressions', 'Clicks', 'Conversions'],
        'Value': [
            df['Impressions'].sum(),
            df['Clicks'].sum(),
            df['Conversions'].sum()
        ]
    })
    
    # Create data sheet for chart
    sheet_name = 'FunnelData'
    data_sheet = workbook.add_worksheet(sheet_name)
    data_sheet.write(0, 0, 'Stage')
    data_sheet.write(0, 1, 'Value')
    
    for idx, row in funnel_data.iterrows():
        data_sheet.write(idx + 1, 0, row['Stage'])
        data_sheet.write(idx + 1, 1, row['Value'])
    
    chart = workbook.add_chart({'type': 'column'})
    chart.add_series({
        'name': 'Conversion Funnel',
        'categories': [sheet_name, 1, 0, len(funnel_data), 0],
        'values': [sheet_name, 1, 1, len(funnel_data), 1],
    })
    chart.set_title({'name': 'Conversion Funnel'})
    chart.set_x_axis({'name': 'Stage'})
    chart.set_y_axis({'name': 'Count'})
    charts_ws.insert_chart(chart_row, 1, chart)
    return chart_row + 18

def insert_geo_performance_chart(workbook, charts_ws, df, chart_row):
    # Aggregate performance by region
    df['Region'] = df['Campaign Name'].apply(lambda x: 'India' if 'India' in str(x) else 'US' if 'US' in str(x) else 'Other')
    geo_performance = df.groupby('Region').agg({
        'ROAS': 'mean',
        'CTR': 'mean',
        'CPC': 'mean'
    }).reset_index()
    
    # Create data sheet for chart
    sheet_name = 'GeoPerformanceData'
    data_sheet = workbook.add_worksheet(sheet_name)
    data_sheet.write(0, 0, 'Region')
    data_sheet.write(0, 1, 'ROAS')
    data_sheet.write(0, 2, 'CTR')
    data_sheet.write(0, 3, 'CPC')
    
    for idx, row in geo_performance.iterrows():
        data_sheet.write(idx + 1, 0, row['Region'])
        data_sheet.write(idx + 1, 1, row['ROAS'])
        data_sheet.write(idx + 1, 2, row['CTR'])
        data_sheet.write(idx + 1, 3, row['CPC'])
    
    chart = workbook.add_chart({'type': 'column'})
    chart.add_series({
        'name': 'ROAS',
        'categories': [sheet_name, 1, 0, len(geo_performance), 0],
        'values': [sheet_name, 1, 1, len(geo_performance), 1],
    })
    chart.add_series({
        'name': 'CTR',
        'categories': [sheet_name, 1, 0, len(geo_performance), 0],
        'values': [sheet_name, 1, 2, len(geo_performance), 2],
    })
    chart.add_series({
        'name': 'CPC',
        'categories': [sheet_name, 1, 0, len(geo_performance), 0],
        'values': [sheet_name, 1, 3, len(geo_performance), 3],
    })
    chart.set_title({'name': 'Regional Performance Comparison'})
    charts_ws.insert_chart(chart_row, 1, chart)
    return chart_row + 18

def generate_recommendations(df: pd.DataFrame) -> List[str]:
    recommendations = []
    
    # Analyze campaign performance
    campaign_metrics = df.groupby('Campaign Name').agg({
        'ROAS': 'mean',
        'CTR': 'mean',
        'CPC': 'mean',
        'Cost': 'sum',
        'Conversions': 'sum',
        'Revenue': 'sum'
    })
    
    # Find high-cost, low-ROAS campaigns
    high_cost_low_roas = campaign_metrics[
        (campaign_metrics['Cost'] > campaign_metrics['Cost'].mean()) &
        (campaign_metrics['ROAS'] < campaign_metrics['ROAS'].mean())
    ]
    
    if not high_cost_low_roas.empty:
        worst_campaign = high_cost_low_roas['ROAS'].idxmin()
        best_campaign = campaign_metrics['ROAS'].idxmax()
        recommendations.append(
            f"🚨 Budget Optimization: Campaign '{worst_campaign}' has high cost (${campaign_metrics.loc[worst_campaign, 'Cost']:,.2f}) but low ROAS ({campaign_metrics.loc[worst_campaign, 'ROAS']:.2f}). Consider reallocating budget to '{best_campaign}' (ROAS: {campaign_metrics.loc[best_campaign, 'ROAS']:.2f})."
        )
    
    # Analyze regional performance
    df['Region'] = df['Campaign Name'].apply(lambda x: 'India' if 'India' in str(x) else 'US' if 'US' in str(x) else 'Other')
    regional_performance = df.groupby('Region').agg({
        'ROAS': 'mean',
        'CTR': 'mean',
        'CPC': 'mean',
        'Cost': 'sum',
        'Revenue': 'sum'
    })
    
    if 'India' in regional_performance.index and 'US' in regional_performance.index:
        india_roas = regional_performance.loc['India', 'ROAS']
        us_roas = regional_performance.loc['US', 'ROAS']
        if india_roas > us_roas:
            recommendations.append(
                f"🌏 Regional Strategy: India market is outperforming US market (ROAS: {india_roas:.2f} vs {us_roas:.2f}). Consider increasing India budget allocation by 20-30%."
            )
        else:
            recommendations.append(
                f"🌎 Regional Strategy: US market is outperforming India market (ROAS: {us_roas:.2f} vs {india_roas:.2f}). Consider increasing US budget allocation by 20-30%."
            )
    
    # Analyze platform performance
    platform_performance = df.groupby('Campaign Name').agg({
        'ROAS': 'mean',
        'CTR': 'mean',
        'CPC': 'mean',
        'Cost': 'sum',
        'Revenue': 'sum'
    })
    
    google_campaigns = platform_performance[platform_performance.index.str.contains('Google', case=False)]
    meta_campaigns = platform_performance[platform_performance.index.str.contains('Meta', case=False)]
    linkedin_campaigns = platform_performance[platform_performance.index.str.contains('LinkedIn', case=False)]
    
    if not google_campaigns.empty and not meta_campaigns.empty:
        google_roas = google_campaigns['ROAS'].mean()
        meta_roas = meta_campaigns['ROAS'].mean()
        if google_roas > meta_roas:
            recommendations.append(
                f"🔍 Platform Optimization: Google Ads campaigns are performing better than Meta Ads (ROAS: {google_roas:.2f} vs {meta_roas:.2f}). Consider reallocating 15-20% of Meta budget to Google."
            )
        else:
            recommendations.append(
                f"🔍 Platform Optimization: Meta Ads campaigns are performing better than Google Ads (ROAS: {meta_roas:.2f} vs {google_roas:.2f}). Consider reallocating 15-20% of Google budget to Meta."
            )
    
    # Add funnel optimization recommendations
    overall_ctr = df['Clicks'].sum() / df['Impressions'].sum()
    overall_cvr = df['Conversions'].sum() / df['Clicks'].sum()
    
    if overall_ctr < 0.02:  # 2% CTR threshold
        recommendations.append(
            f"🎯 Ad Performance: Low CTR detected ({overall_ctr:.2%}). Consider:\n"
            "1. Reviewing ad copy for clarity and relevance\n"
            "2. Testing new ad creatives\n"
            "3. Refining audience targeting"
        )
    if overall_cvr < 0.05:  # 5% CVR threshold
        recommendations.append(
            f"🎯 Conversion Optimization: Low conversion rate detected ({overall_cvr:.2%}). Consider:\n"
            "1. Reviewing landing page user experience\n"
            "2. Testing different CTAs\n"
            "3. Implementing A/B testing for key elements"
        )
    
    # Add cost efficiency recommendations
    avg_cpc = df['CPC'].mean()
    if avg_cpc > df['CPC'].median() * 1.5:
        recommendations.append(
            f"💰 Cost Efficiency: High average CPC (${avg_cpc:.2f}). Consider:\n"
            "1. Reviewing keyword quality scores\n"
            "2. Optimizing ad relevance\n"
            "3. Adjusting bid strategies"
        )
    
    # Add revenue optimization recommendations
    best_campaign = campaign_metrics['ROAS'].idxmax()
    best_roas = campaign_metrics.loc[best_campaign, 'ROAS']
    if best_roas > 3.0:  # Good ROAS threshold
        recommendations.append(
            f"💎 Revenue Opportunity: Campaign '{best_campaign}' shows excellent performance (ROAS: {best_roas:.2f}). Consider:\n"
            "1. Scaling this campaign by 30-40%\n"
            "2. Analyzing and replicating its successful elements\n"
            "3. Testing similar audience segments"
        )
    
    return recommendations 