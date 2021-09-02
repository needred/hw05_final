from django.shortcuts import render


def page_not_found_view(request, exception):
    """
    Отображаем страницу 404.
    """
    return render(request, "errors/404.html",
                  {"path": request.path}, status=404)


def my_custom_error_view(request):
    """
    Отображаем страницу 500.
    """
    return render(request, "errors/500.html", status=500)


def csrf_failure(request, reason=''):
    """
    Отображаем страницу 403.
    """
    return render(request, 'errors/403csrf.html')
