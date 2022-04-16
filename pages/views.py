from django.shortcuts import render, HttpResponse

# Create your views here.


def index(request):
	context = {
		'page_title': 'Home',
	}

	return render(request, 'pages/index.html', context)


def about(request):
	context = {
		'page_title': 'About',
	}

	return render(request, 'pages/about.html', context)
