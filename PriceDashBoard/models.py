from django.db import models

# Create your models here.
class MaterialsModel(models.Model):
    material_name = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.material_name}'


class MaterialsPriceModel(models.Model):
    material_name = models.ForeignKey(MaterialsModel, on_delete=models.CASCADE)
    date = models.DateField()
    price = models.FloatField()
    
    def __str__(self):
        return f'{self.date} 자 {self.material_name} 가격 : {self.price}'
    


