from django.db import models

class Item(models.Model):
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
    item = models.ForeignKey("Item", on_delete=models.CASCADE)
    qty = models.IntegerField()

    class Meta:
        db_table = "order_details"


    