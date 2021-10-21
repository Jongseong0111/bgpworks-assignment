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

    @query_debugger
    def put(self, request):
        with transaction.atomic():
            data = json.loads(request.body)

            order_id = data['order_id']
            type = data['type']
            items = data['items']
            
            order_details = OrderDetail.objects.filter(order_id = order_id)
            for order_detail in order_details:
                item = Item.objects.get(id = order_detail.item_id)
                item.qty -= order_detail.qty
                item.save()
                order_detail.qty = 0
                order_detail.save()

            for item in items:
                item_id = item['item_id']
                qty = item['quantity']

                if not Item.objects.filter(id=item_id).exists():
                    Item.objects.create(id = item_id, qty = qty)
                else:
                    old_item = Item.objects.get(id=item_id)
                    old_item.qty += qty
                    old_item.save()
                if not OrderDetail.objects.filter(order_id = order_id, item_id=item_id).exists():
                    OrderDetail.objects.create(item_id = item_id, qty=qty, order_id=order_id)
                else:
                    order_detail = OrderDetail.objects.get(order_id = order_id, item_id = item_id)
                    order_detail.qty = qty
                    order_detail.save()
                    
            return JsonResponse({'MESSAGE': "SUCCESS"}, status=201)
            



            