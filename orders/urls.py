from django.urls        import path
from orders.views   import ReceiptView

urlpatterns = [
    path('', ReceiptView.as_view())
]
