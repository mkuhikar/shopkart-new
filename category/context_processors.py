from .models import Category

# We are using this to access categories in all pages
def menu_links(request):
    links=Category.objects.all()
    return dict(links=links)
