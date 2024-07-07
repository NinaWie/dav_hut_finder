from django.shortcuts import render
from .models import Hut

def search_view(request):
    all_huts = Hut.objects.all()
    context = {'count': all_huts.count()}
    return render(request, 'hut_finder/search.html', context)


def search_results_view(request):
    query = request.GET.get('search', '')
    print(f'{request} {query = }')

    all_huts = Hut.objects.all()
    if query:
        huts = all_huts.filter(name__icontains=query)
    else:
        huts = []

    context = {'huts': huts, 'count': all_huts.count()}
    return render(request, 'hut_finder/search_results.html', context)