import functions_framework
# Dummy cloud function
@functions_framework.http
def handler(request):
    return "Hello world"