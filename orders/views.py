import json

from django.http      import JsonResponse
from django.views     import View
from django.db        import transaction

from orders.models     import Item, Order, OrderDetail
from decorators       import query_debugger

class ReceiptView(View):
    @query_debugger
    def post(self, request):
        with transaction.atomic():
            data = json.loads(request.body)

            time = data['time']
            type = data['type']
            items = data['items']

            order = Order.objects.create(
                time = time, 
                type = type
                )

            for item in items:
                item_id = item['item_id']
                qty = item['quantity']
                if not Item.objects.filter(id=item_id).exists():
                    Item.objects.create(id = item_id, qty = qty)
                else:
                    old_item = Item.objects.get(id=item_id)
                    old_item.qty += qty
                    old_item.save()
                OrderDetail.objects.create(item_id = item_id, qty=qty, order=order)

            return JsonResponse({'MESSAGE': "SUCCESS"}, status=201)

    def put(self, request):
        with transaction.atomic():
            data = json.loads(request.body)
