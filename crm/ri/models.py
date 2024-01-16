from django.db import models
from django.contrib.auth.models import User

class Warehouse(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()

    def __str__(self):
        return self.name

class Unit(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Good(models.Model):
    name = models.CharField(max_length=255)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Counterparty(models.Model):
    name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    id_card = models.CharField(max_length=20)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.id_card})"

    class Meta:
        verbose_name_plural = "Counterparties"

class Doctype(models.Model):
    name = models.CharField(max_length=255, default='')

    def __str__(self):
        return self.name

class Documents(models.Model):
    Date = models.DateTimeField()
    Title = models.CharField(max_length=255)
    Doctype = models.ForeignKey(Doctype, on_delete=models.CASCADE, default=1)
    Author = models.ForeignKey(User, on_delete=models.CASCADE)
    Warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    Counterparty = models.ForeignKey(Counterparty, on_delete=models.CASCADE)
    Amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.Title} ({self.Date})"

    class Meta:
        verbose_name_plural = "Documents"


class Goods_in_stock(models.Model):
    Date = models.DateField()
    Document = models.ForeignKey(Documents, on_delete=models.CASCADE)
    Good = models.ForeignKey(Good, on_delete=models.CASCADE)
    Unit = models.ForeignKey(Unit, on_delete=models.CASCADE, default=1)
    Warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    Income = models.BooleanField()
    Quantity = models.DecimalField(max_digits=10, decimal_places=2)
    Sum = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.Good} - {self.Quantity} ({self.Date})"


class Sales(models.Model):
    Date = models.DateField()
    Document = models.ForeignKey(Documents, on_delete=models.CASCADE)
    Good = models.ForeignKey(Good, on_delete=models.CASCADE)
    Counterparty = models.ForeignKey(Counterparty, on_delete=models.CASCADE)
    Income = models.BooleanField()
    Quantity = models.DecimalField(max_digits=10, decimal_places=2)
    Amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.Good} - {self.Quantity} ({self.Date})"

    class Meta:
        verbose_name_plural = "Sales"
