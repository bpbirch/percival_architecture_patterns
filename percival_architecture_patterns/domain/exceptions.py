
class OutOfStock(Exception):
    "raise when OrderLine.qty > Batch.qty"
    pass

class SkuMismatch(Exception):
    "raise when OrderLine.sku != Batch.sku"