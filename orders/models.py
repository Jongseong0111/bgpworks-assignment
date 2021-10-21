from django.db import models

class Item(models.Model):
    item_id = models.IntegerField()
    qty = models.IntegerField()

    class Meta:
        db_table = "items"

class Order(models.Model):
    time = models.DateTimeField()
    type = models.IntegerField()

    class Meta:
        db_table = "orders"

class OrderDetail(models.Model):
    order = models.ForeignKey("Order", on_delete=models.CASCADE)
    item_id = models.IntegerField()
    qty = models.IntegerField()

    class Meta:
        db_table = "order_details"


    