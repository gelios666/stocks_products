from rest_framework import serializers
from .models import Product, Stock, StockProduct


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description']


class StockProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = StockProduct
        fields = ['product', 'quantity', 'price']


class StockSerializer(serializers.ModelSerializer):
    products = StockProductSerializer(source='positions', many=True)

    class Meta:
        model = Stock
        fields = ['id', 'address', 'products']

    def create(self, validated_data):
        products_data = validated_data.pop('positions')
        stock = Stock.objects.create(**validated_data)

        for item in products_data:
            product_data = item.pop('product')
            product, _ = Product.objects.get_or_create(**product_data)

            StockProduct.objects.create(
                stock=stock,
                product=product,
                quantity=item.get('quantity'),
                price=item.get('price'),
            )

        return stock

    def update(self, instance, validated_data):
        products_data = validated_data.pop('positions', [])
        instance.address = validated_data.get('address', instance.address)
        instance.save()

        for item in products_data:
            product_data = item.pop('product')
            product, _ = Product.objects.get_or_create(**product_data)

            StockProduct.objects.update_or_create(
                stock=instance,
                product=product,
                defaults={
                    'quantity': item.get('quantity'),
                    'price': item.get('price'),
                }
            )

        return instance
