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

            # order 생성
            order = Order.objects.create(
                time = time, 
                type = type
                )

            
            # 생성한 order의 id로 order detail 배열 생성
            new_order_detail = []
            for item in items:
                item_id = item['item_id']
                qty = item['quantity']
                new_order_detail.append(OrderDetail(order_id = order.id, item_id = item_id, qty = qty))

            # order detail bulk create
            OrderDetail.objects.bulk_create(new_order_detail)
            # 존재하는 id 뽑아내기
            ids_list = [item['item_id'] for item in items]

            ids = Item.objects.filter(item_id__in = ids_list)
            old_ids = [item.item_id for item in ids]
            old_qty = []

            # 존재하는 id는 update, 존재하지 않는 id는 create 배열에 나눠담기
            new_items = []
            old_items = []
            for item in items:
                item_id = item['item_id']
                qty = item['quantity']

                if item_id in old_ids:
                    old_items.append(item_id)
                    old_qty.append(qty)
                else:
                    new_items.append(Item(item_id = item_id, qty = qty) )
            
            # 존재하지 않는 id에 대해 bulk_create
            Item.objects.bulk_create(new_items)
            
            # 존재하는 id에 대해 bulk_update
            for index in range(len(ids)):
                ids[index].qty += old_qty[index]
                
            Item.objects.bulk_update(ids, ['qty'])



            # ### 

            # id_list = [item['item_id'] for item in items]
            # new_item = []
            # old_item = []
            # new_order_detail = []

            
            # for item in items:
            #     item_id = item['item_id']
            #     qty = item['quantity']
                
            #     if not Item.objects.filter(item_id = item_id).exists():
            #         new_item.append(Item(item_id = item_id, qty = qty))

            #     else:
            #         old_item.append((item_id, qty))
            # # 존재하지 않던 Item 생성
            # Item.objects.bulk_create(new_item)

            # if old_item!=[]:
            #     ids = [i[0] for i in old_item]
            #     qtys = [i[1] for i in old_item]
            #     old_items = Item.objects.filter(item_id__in = ids)

            #     for i in range(len(old_items)):
            #         old_items[i].qty += qtys[i]
            
            #     Item.objects.bulk_update(old_items, ['qty'] )
            # print(id_list)
            # item_ids = Item.objects.filter(item_id__in = id_list)
            # print(len(item_ids))
            # id_lists = [item.id for item in item_ids]
            # for i in range(len(items)):
            #     id = id_lists[i]
            #     qty = items[i]['quantity']
            #     # Order Detail를 생성하기 위해 배열에 담기
            #     new_order_detail.append(OrderDetail(order_id = order.id, item_id = id, qty = qty))

            # OrderDetail.objects.bulk_create(new_order_detail)
            return JsonResponse({'MESSAGE': "SUCCESS"}, status=201)

    @query_debugger
    def patch(self, request):
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
            
            result = []
            stocks = Item.objects.exclude(qty=0)
            for stock in stocks:
                result.append({"item_id" : stock.id, "quantity" : stock.qty})

            return JsonResponse({'RESULT': result}, status=200)
            
