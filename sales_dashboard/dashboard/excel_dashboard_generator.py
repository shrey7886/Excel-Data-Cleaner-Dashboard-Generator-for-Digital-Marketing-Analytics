import pandas as pd
import numpy as np
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, LineChart, PieChart, ScatterChart
from openpyxl.chart.series import DataPoint
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.worksheet.dimensions import ColumnDimension, DimensionHolder
from openpyxl.worksheet.worksheet import Worksheet
from datetime import datetime, timedelta
import os
import json

class ExcelDashboardGenerator:
    def __init__(self):
        self.wb = Workbook()
        self.ws = self.wb.active
        self.ws.title = "Dashboard"
        
        # Define styles
        self.header_font = Font(bold=True, size=14, color="FFFFFF")
        self.subheader_font = Font(bold=True, size=12, color="FFFFFF")
        self.title_font = Font(bold=True, size=16, color="2E86AB")
        self.normal_font = Font(size=10)
        
        self.header_fill = PatternFill(start_color="2E86AB", end_color="2E86AB", fill_type="solid")
        self.subheader_fill = PatternFill(start_color="A23B72", end_color="A23B72", fill_type="solid")
        self.success_fill = PatternFill(start_color="28A745", end_color="28A745", fill_type="solid")
        self.warning_fill = PatternFill(start_color="FFC107", end_color="FFC107", fill_type="solid")
        self.danger_fill = PatternFill(start_color="DC3545", end_color="DC3545", fill_type="solid")
        
        self.border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
    def create_dashboard(self, data, predictions=None, insights=None, client_name="Client"):
        """Create a comprehensive Excel dashboard"""
        self.client_name = client_name
        self.data = data
        self.predictions = predictions or {}
        self.insights = insights or {}
        
        # Create different sections
        self.create_header()
        self.create_summary_section()
        self.create_kpi_section()
        self.create_data_section()
        self.create_charts_section()
        self.create_predictions_section()
        self.create_insights_section()
        self.create_recommendations_section()
        
        # Auto-adjust column widths
        self.auto_adjust_columns()
        
        return self.wb
    
    def create_header(self):
        """Create the dashboard header"""
        # Title
        self.ws['A1'] = f"Targetorate - {self.client_name} Marketing Analytics Dashboard"
        self.ws['A1'].font = Font(bold=True, size=20, color="2E86AB")
        self.ws.merge_cells('A1:H1')
        # Logo placeholder (optional)
        # self.ws.add_image(Image('logo.png'), 'I1')  # Uncomment and provide logo if desired
        # Generated date
        self.ws['A2'] = f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        self.ws['A2'].font = Font(italic=True, size=10, color="666666")
        self.ws.merge_cells('A2:H2')
        # Add some spacing
        self.ws['A4'] = ""
        self.ws.row_dimensions[1].height = 28
        self.ws.row_dimensions[2].height = 18
        self.ws.row_dimensions[4].height = 8

    def create_summary_section(self):
        """Create summary statistics section"""
        row = 5
        
        # Section header
        self.ws[f'A{row}'] = "📊 EXECUTIVE SUMMARY"
        self.ws[f'A{row}'].font = self.title_font
        self.ws.merge_cells(f'A{row}:H{row}')
        self.ws.row_dimensions[row].height = 22
        
        row += 2
        
        # Calculate summary stats
        if not self.data.empty:
            total_spend = self.data.get('spend', pd.Series([0])).sum()
            total_revenue = self.data.get('revenue', pd.Series([0])).sum()
            total_clicks = self.data.get('clicks', pd.Series([0])).sum()
            total_impressions = self.data.get('impressions', pd.Series([0])).sum()
            total_conversions = self.data.get('conversions', pd.Series([0])).sum()
            
            roas = total_revenue / total_spend if total_spend > 0 else 0
            ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
            cpa = total_spend / total_conversions if total_conversions > 0 else 0
            
            # Summary table
            summary_data = [
                ["Metric", "Value", "Status"],
                ["Total Spend", f"${total_spend:,.2f}", "💰"],
                ["Total Revenue", f"${total_revenue:,.2f}", "💵"],
                ["ROAS", f"{roas:.2f}x", "📈" if roas > 1 else "📉"],
                ["Click-Through Rate", f"{ctr:.2f}%", "✅" if ctr > 2 else "⚠️"],
                ["Conversion Rate", f"{conversion_rate:.2f}%", "✅" if conversion_rate > 2 else "⚠️"],
                ["Cost Per Acquisition", f"${cpa:.2f}", "✅" if cpa < 50 else "⚠️"],
                ["Total Clicks", f"{total_clicks:,}", "📊"],
                ["Total Impressions", f"{total_impressions:,}", "👁️"],
                ["Total Conversions", f"{total_conversions:,}", "🎯"]
            ]
            
            for i, row_data in enumerate(summary_data):
                for j, cell_value in enumerate(row_data):
                    cell = self.ws.cell(row=row + i, column=j + 1, value=cell_value)
                    if i == 0:  # Header row
                        cell.font = self.header_font
                        cell.fill = self.header_fill
                        cell.alignment = Alignment(horizontal='center')
                    else:
                        cell.font = self.normal_font
                        cell.border = self.border
                        if j == 0:  # Metric column
                            cell.font = Font(bold=True, size=10)
                        elif j == 2:  # Status column
                            cell.alignment = Alignment(horizontal='center')
                        elif j == 1:
                            cell.alignment = Alignment(horizontal='right')
                self.ws.row_dimensions[row + i].height = 18
            
            # Freeze header row
            self.ws.freeze_panes = self.ws['A7']
            row += len(summary_data) + 2
        
        # Add spacing
        self.ws[f'A{row}'] = ""
        self.ws.row_dimensions[row].height = 8
        return row + 1
    
    def create_kpi_section(self):
        """Create KPI cards section"""
        row = 20
        
        # Section header
        self.ws[f'A{row}'] = "🎯 KEY PERFORMANCE INDICATORS"
        self.ws[f'A{row}'].font = self.title_font
        self.ws.merge_cells(f'A{row}:H{row}')
        
        row += 2
        
        if not self.data.empty:
            # Calculate KPIs by platform
            platforms = self.data.get('platform', pd.Series(['Unknown'])).unique()
            
            for i, platform in enumerate(platforms):
                platform_data = self.data[self.data.get('platform', pd.Series(['Unknown'])) == platform]
                
                if not platform_data.empty:
                    spend = platform_data.get('spend', pd.Series([0])).sum()
                    revenue = platform_data.get('revenue', pd.Series([0])).sum()
                    clicks = platform_data.get('clicks', pd.Series([0])).sum()
                    impressions = platform_data.get('impressions', pd.Series([0])).sum()
                    
                    roas = revenue / spend if spend > 0 else 0
                    ctr = (clicks / impressions * 100) if impressions > 0 else 0
                    
                    # Platform KPI card
                    col_offset = (i % 2) * 4
                    start_col = 1 + col_offset
                    
                    # Platform name
                    self.ws.cell(row=row, column=start_col, value=f"📱 {platform.upper()}")
                    self.ws.cell(row=row, column=start_col).font = self.subheader_font
                    self.ws.cell(row=row, column=start_col).fill = self.subheader_fill
                    self.ws.merge_cells(f'{chr(64+start_col)}{row}:{chr(64+start_col+3)}{row}')
                    
                    row += 1
                    
                    # KPI values
                    kpis = [
                        ["Spend", f"${spend:,.2f}"],
                        ["Revenue", f"${revenue:,.2f}"],
                        ["ROAS", f"{roas:.2f}x"],
                        ["CTR", f"{ctr:.2f}%"]
                    ]
                    
                    for j, (kpi_name, kpi_value) in enumerate(kpis):
                        self.ws.cell(row=row+j, column=start_col, value=kpi_name).font = Font(bold=True)
                        self.ws.cell(row=row+j, column=start_col+1, value=kpi_value)
                        self.ws.cell(row=row+j, column=start_col+2, value="✅" if roas > 1 else "⚠️")
                        
                        # Add borders
                        for col in range(start_col, start_col+3):
                            self.ws.cell(row=row+j, column=col).border = self.border
                    
                    row += len(kpis) + 1
                    
                    if i % 2 == 1:  # Move to next row for next platform
                        row += 2
        
        return row + 2
    
    def create_data_section(self):
        """Create raw data section"""
        row = 35
        
        # Section header
        self.ws[f'A{row}'] = "📋 RAW DATA"
        self.ws[f'A{row}'].font = self.title_font
        self.ws.merge_cells(f'A{row}:H{row}')
        self.ws.row_dimensions[row].height = 22
        
        row += 2
        
        if not self.data.empty:
            # Add data to worksheet
            for r_idx, r in enumerate(dataframe_to_rows(self.data.head(100), index=False, header=True)):
                for j, value in enumerate(r, 1):
                    cell = self.ws.cell(row=row + r_idx, column=j, value=value)
                    if r_idx == 0:
                        cell.font = self.header_font
                        cell.fill = self.header_fill
                        cell.alignment = Alignment(horizontal='center')
                    else:
                        cell.font = self.normal_font
                        cell.border = self.border
                        # Zebra striping
                        if r_idx % 2 == 1:
                            cell.fill = PatternFill(start_color="F7F7F7", end_color="F7F7F7", fill_type="solid")
                        # Center-align numbers, right-align currency
                        if isinstance(value, (int, float)):
                            cell.alignment = Alignment(horizontal='center')
                        elif isinstance(value, str) and value.startswith('$'):
                            cell.alignment = Alignment(horizontal='right')
                self.ws.row_dimensions[row + r_idx].height = 16
            
            # Add filters
            self.ws.auto_filter.ref = f"A{row}:H{row + r_idx}"
            # Freeze header row
            self.ws.freeze_panes = self.ws[f'A{row + 1}']
            row += r_idx + 1
            
            # Add note about data truncation
            if len(self.data) > 100:
                self.ws[f'A{row}'] = f"Note: Showing first 100 rows of {len(self.data)} total records"
                self.ws[f'A{row}'].font = Font(italic=True, size=9, color="666666")
                self.ws.merge_cells(f'A{row}:H{row}')
                self.ws.row_dimensions[row].height = 14
        
        self.ws[f'A{row + 2}'] = ""
        self.ws.row_dimensions[row + 2].height = 8
        return row + 3
    
    def create_charts_section(self):
        """Create charts section"""
        row = 50
        
        # Section header
        self.ws[f'A{row}'] = "📈 PERFORMANCE CHARTS"
        self.ws[f'A{row}'].font = self.title_font
        self.ws.merge_cells(f'A{row}:H{row}')
        
        row += 2
        
        if not self.data.empty:
            # Create charts worksheet
            charts_ws = self.wb.create_sheet("Charts")
            
            # Chart 1: Spend by Platform
            if 'platform' in self.data.columns and 'spend' in self.data.columns:
                spend_by_platform = self.data.groupby('platform')['spend'].sum()
                
                # Add data to charts worksheet
                charts_ws['A1'] = "Platform"
                charts_ws['B1'] = "Spend"
                
                for i, (platform, spend) in enumerate(spend_by_platform.items(), 2):
                    charts_ws[f'A{i}'] = platform
                    charts_ws[f'B{i}'] = spend
                
                # Create bar chart
                chart1 = BarChart()
                chart1.title = "Spend by Platform"
                chart1.x_axis.title = "Platform"
                chart1.y_axis.title = "Spend ($)"
                
                data = charts_ws['B2:B{}'.format(len(spend_by_platform) + 1)]
                cats = charts_ws['A2:A{}'.format(len(spend_by_platform) + 1)]
                chart1.add_data(data, titles_from_data=True)
                chart1.set_categories(cats)
                
                charts_ws.add_chart(chart1, "D2")
            
            # Chart 2: Revenue Trend (if date column exists)
            if 'date' in self.data.columns and 'revenue' in self.data.columns:
                try:
                    self.data['date'] = pd.to_datetime(self.data['date'])
                    revenue_trend = self.data.groupby(self.data['date'].dt.date)['revenue'].sum()
                    
                    # Add data to charts worksheet
                    charts_ws['A10'] = "Date"
                    charts_ws['B10'] = "Revenue"
                    
                    for i, (date, revenue) in enumerate(revenue_trend.items(), 11):
                        charts_ws[f'A{i}'] = date
                        charts_ws[f'B{i}'] = revenue
                    
                    # Create line chart
                    chart2 = LineChart()
                    chart2.title = "Revenue Trend"
                    chart2.x_axis.title = "Date"
                    chart2.y_axis.title = "Revenue ($)"
                    
                    data = charts_ws['B11:B{}'.format(len(revenue_trend) + 10)]
                    cats = charts_ws['A11:A{}'.format(len(revenue_trend) + 10)]
                    chart2.add_data(data, titles_from_data=True)
                    chart2.set_categories(cats)
                    
                    charts_ws.add_chart(chart2, "D10")
                except:
                    pass
        
        return row + 2
    
    def create_predictions_section(self):
        """Create predictions section on a separate worksheet"""
        # Create or get the predictions worksheet
        if 'Predictions' in self.wb.sheetnames:
            pred_ws = self.wb['Predictions']
        else:
            pred_ws = self.wb.create_sheet('Predictions')
        row = 1
        # Section header
        pred_ws[f'A{row}'] = "🔮 AI PREDICTIONS & FORECASTS"
        pred_ws[f'A{row}'].font = self.title_font
        pred_ws.merge_cells(f'A{row}:H{row}')
        pred_ws.row_dimensions[row].height = 22
        row += 2
        if self.predictions:
            for pred_type, pred_data in self.predictions.items():
                pred_ws[f'A{row}'] = f"📊 {pred_type.upper()}"
                pred_ws[f'A{row}'].font = self.subheader_font
                pred_ws[f'A{row}'].fill = self.subheader_fill
                pred_ws.merge_cells(f'A{row}:H{row}')
                row += 1
                if isinstance(pred_data, dict):
                    for key, value in pred_data.items():
                        pred_ws[f'A{row}'] = key.replace('_', ' ').title()
                        pred_ws[f'B{row}'] = str(value)
                        pred_ws[f'A{row}'].font = Font(bold=True)
                        row += 1
                else:
                    pred_ws[f'A{row}'] = str(pred_data)
                    row += 1
                row += 1
        else:
            pred_ws[f'A{row}'] = "No predictions available yet. Upload more data to generate AI insights."
            pred_ws[f'A{row}'].font = Font(italic=True, color="666666")
            pred_ws.merge_cells(f'A{row}:H{row}')
        # Auto-adjust columns
        for column in pred_ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            pred_ws.column_dimensions[column_letter].width = adjusted_width
        # Set print setup
        pred_ws.page_setup.orientation = 'landscape'
        pred_ws.page_setup.fitToWidth = 1
        pred_ws.page_setup.fitToHeight = 0
        return row + 2
    
    def create_insights_section(self):
        """Create insights section"""
        row = 70
        
        # Section header
        self.ws[f'A{row}'] = "💡 AI INSIGHTS & ANALYSIS"
        self.ws[f'A{row}'].font = self.title_font
        self.ws.merge_cells(f'A{row}:H{row}')
        
        row += 2
        
        if self.insights:
            for insight_type, insight_data in self.insights.items():
                # Insight type header
                self.ws[f'A{row}'] = f"🔍 {insight_type.upper()}"
                self.ws[f'A{row}'].font = self.subheader_font
                self.ws[f'A{row}'].fill = self.subheader_fill
                self.ws.merge_cells(f'A{row}:H{row}')
                
                row += 1
                
                # Add insight details
                if isinstance(insight_data, list):
                    for insight in insight_data:
                        self.ws[f'A{row}'] = f"• {insight}"
                        self.ws[f'A{row}'].font = self.normal_font
                        self.ws.merge_cells(f'A{row}:H{row}')
                        row += 1
                else:
                    self.ws[f'A{row}'] = str(insight_data)
                    self.ws[f'A{row}'].font = self.normal_font
                    self.ws.merge_cells(f'A{row}:H{row}')
                    row += 1
                
                row += 1
        else:
            self.ws[f'A{row}'] = "No insights available yet. Upload more data to generate AI analysis."
            self.ws[f'A{row}'].font = Font(italic=True, color="666666")
            self.ws.merge_cells(f'A{row}:H{row}')
        
        return row + 2
    
    def create_recommendations_section(self):
        """Create recommendations section"""
        row = 80
        
        # Section header
        self.ws[f'A{row}'] = "🚀 STRATEGIC RECOMMENDATIONS"
        self.ws[f'A{row}'].font = self.title_font
        self.ws.merge_cells(f'A{row}:H{row}')
        
        row += 2
        
        # Generate recommendations based on data
        recommendations = self.generate_recommendations()
        
        for i, rec in enumerate(recommendations, 1):
            self.ws[f'A{row}'] = f"{i}. {rec}"
            self.ws[f'A{row}'].font = self.normal_font
            self.ws.merge_cells(f'A{row}:H{row}')
            row += 1
        
        return row + 2
    
    def generate_recommendations(self):
        """Generate strategic recommendations based on data"""
        recommendations = []
        
        if not self.data.empty:
            # Calculate key metrics
            total_spend = self.data.get('spend', pd.Series([0])).sum()
            total_revenue = self.data.get('revenue', pd.Series([0])).sum()
            roas = total_revenue / total_spend if total_spend > 0 else 0
            
            # Platform-specific recommendations
            if 'platform' in self.data.columns:
                platform_performance = self.data.groupby('platform').agg({
                    'spend': 'sum',
                    'revenue': 'sum',
                    'clicks': 'sum',
                    'impressions': 'sum'
                }).reset_index()
                
                platform_performance['roas'] = platform_performance['revenue'] / platform_performance['spend']
                platform_performance['ctr'] = (platform_performance['clicks'] / platform_performance['impressions'] * 100)
                
                best_platform = platform_performance.loc[platform_performance['roas'].idxmax()]
                worst_platform = platform_performance.loc[platform_performance['roas'].idxmin()]
                
                recommendations.extend([
                    f"Focus budget allocation on {best_platform['platform']} (ROAS: {best_platform['roas']:.2f}x)",
                    f"Optimize campaigns on {worst_platform['platform']} to improve ROAS (currently {worst_platform['roas']:.2f}x)",
                ])
            
            # General recommendations
            if roas < 1:
                recommendations.append("Consider reducing spend or optimizing campaigns to improve ROAS")
            elif roas > 2:
                recommendations.append("Consider increasing budget allocation to high-performing campaigns")
            
            if 'ctr' in self.data.columns:
                avg_ctr = self.data['ctr'].mean()
                if avg_ctr < 2:
                    recommendations.append("Improve ad creative and targeting to increase click-through rates")
            
            if 'conversion_rate' in self.data.columns:
                avg_conversion = self.data['conversion_rate'].mean()
                if avg_conversion < 2:
                    recommendations.append("Optimize landing pages and user experience to improve conversion rates")
        
        # Add default recommendations if none generated
        if not recommendations:
            recommendations = [
                "Continue monitoring campaign performance and adjust strategies accordingly",
                "Consider A/B testing different ad creatives and targeting options",
                "Focus on high-converting audience segments",
                "Optimize landing pages for better user experience",
                "Implement retargeting campaigns for better conversion rates"
            ]
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def auto_adjust_columns(self):
        """Auto-adjust column widths"""
        for column in self.ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            
            adjusted_width = min(max_length + 2, 50)
            self.ws.column_dimensions[column_letter].width = adjusted_width
        # Set print setup
        self.ws.page_setup.orientation = 'landscape'
        self.ws.page_setup.fitToWidth = 1
        self.ws.page_setup.fitToHeight = 0
    
    def save_dashboard(self, filename):
        """Save the dashboard to a file"""
        self.wb.save(filename)
        return filename 