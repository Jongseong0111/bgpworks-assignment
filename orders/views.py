import json
import datetime
from datetime import date

from django.http      import JsonResponse
from django.views     import View
from django.db        import transaction
from django.db.models import F, Sum, Count, Case, When, Value
from django.db.models.functions import Coalesce

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
            old_ids = [item.item_id for item in ids] # 캐싱
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
            
            return JsonResponse({'MESSAGE': "SUCCESS"}, status=201)

    @query_debugger
    def patch(self, request):
        with transaction.atomic():
            data = json.loads(request.body)

            order_id = data['order_id']
            type = data['type']
            items = data['items']
            pair = {}
            for item in items:
                pair[item['item_id']] = item['quantity']

            
            # order_id 기준으로 order detail 불러오기

            order_details = OrderDetail.objects.filter(order_id = order_id)

            ids = [order_detail.item_id for order_detail in order_details] # 존재하던 order detail의 item_id
            qtys = [order_detail.qty for order_detail in order_details] # 존재하던 order detail의 qty

            remove_items = []
            # 원복하기 위해 item 불러와서 수정
            old_items = Item.objects.filter(item_id__in = ids) 
            for i in range(len(old_items)):
                old_items[i].qty -= qtys[i] # 기존 order detail의 수량만큼 감소
            

            # Item bulk_update
            Item.objects.bulk_update(old_items, ['qty'])
            
            # 기존 order detail은 update, 새로 들어온 것 중 없는 것은 create

            new_ids = [item['item_id'] for item in items] # 새로 들어온 order의 item_id
            for order_detail in order_details:
                if order_detail.item_id not in new_ids: 
                    order_detail.qty = 0 # 삭제되는 order detail 처리
                else:
                    order_detail.qty = pair[order_detail.item_id] # 업데이트되는 order detail 처리
            
            # Update order detail
            OrderDetail.objects.bulk_update(order_details, ['qty'])

            # Create order detail
            new_order_detail = []
            for item in items:
                item_id = item['item_id']
                qty = item['quantity']
                if item_id not in ids: # 추가되는 order detail
                    new_order_detail.append(OrderDetail(order_id = order_id, item_id = item_id, qty = qty))

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

            result = []
            stocks = Item.objects.exclude(qty=0).order_by('item_id')
            for stock in stocks:
                result.append({"item_id" : stock.item_id, "quantity" : stock.qty})

            return JsonResponse({'RESULT': result}, status=200)
            
    @query_debugger
    def get(self, request):
        result = []
        now_time = date.today()
  
        for i in range(7):
            after = now_time + datetime.timedelta(days=1)
            orders = OrderDetail.objects.annotate(in_q=Sum(Case(When(order__time__range = (now_time, after), order__type = 0,then='qty'), default=0)),\
                    out_q = Sum(Case(When(order__time__range = (now_time, after), order__type=1,then='qty'), default=0 )),\
                    balance_q = Sum(Case(When(order__time__lte = after,then='qty'), default=0)))\
                    .aggregate(in_qty = Sum('in_q'), out_qty = Sum('out_q'), balance = Sum('balance_q'))
            result.append({'date' : now_time, 'in_qty' : orders['in_qty'], 'out_qty' : orders['out_qty'], 'balance' : orders['balance']})
            now_time -= datetime.timedelta(days=1)
        return JsonResponse({'RESULT': result}, status=200)
