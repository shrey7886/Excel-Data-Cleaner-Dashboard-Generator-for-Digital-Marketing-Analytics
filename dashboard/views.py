from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from dashboard.rag_pipeline import rag_answer

@csrf_exempt
def rag_chatbot(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        query = data.get("query", "")
        if not query:
            return JsonResponse({"error": "No query provided."}, status=400)
        answer = rag_answer(query)
        return JsonResponse({"answer": answer})
    return JsonResponse({"error": "POST only."}, status=405) 