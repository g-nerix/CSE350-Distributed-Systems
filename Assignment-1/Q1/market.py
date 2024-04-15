# market.py
# to compile protofile : protoc --proto_path=. --python_out=. ./market.proto
# python -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. market.proto

import grpc
from concurrent import futures
import market_pb2_grpc as proto_grpc
import market_pb2 as proto
import uuid

class MarketService(proto_grpc.MarketServiceServicer):
    def __init__(self):
        # Initialize any necessary state or data structures for the MarketService
        self.sellers = {}  # Placeholder for seller information
        self.items = {}    # Placeholder for item information
        self.wishlist = {} # Placeholder for wishlist items

    def RegisterSeller(self, request, context):
        # Implement logic for seller registration
        seller_info = request.sellerInfo
        seller_address = seller_info.sellerAddress

        if seller_address in self.sellers:
            return proto.Response(message="FAIL: Seller with this address already registered.")

        # seller_id = str(uuid.uuid1())
        seller_id = seller_info.sellerId
        self.sellers[seller_address] = {'id': seller_id, 'info': seller_info}
        
        print(f"Market prints: Seller join request from {seller_info.sellerAddress}, uuid = {seller_id}")
        return proto.Response(message="SUCCESS")

    def UpdateItem(self, request, context):
        item_id = request.itemId
        new_price = request.newPrice
        new_quantity = request.newQuantity
        seller_id = request.seller.sellerId
        print(f'Market : Update Item {item_id} request from {request.seller.sellerAddress}')
        # Check if the item exists and belongs to the seller
        if item_id in self.items:
            item_details = self.items[item_id]
            product = item_details['product']       
            if product.seller.sellerId == seller_id:   
            # Update item details
                product.price = new_price
                product.quantity = new_quantity
                return proto.Response(message="SUCCESS")
            else:
                return proto.Response(message="FAIL seller doesn't own the product")
        else:
            return proto.Response(message="FAIL did not fin the product ID")

    def DisplaySellerItems(self, request, context,verbose = False):
        seller_id = request.sellerInfo.sellerId
        print(f'Market: Display Items request from {request.sellerInfo.sellerAddress}')
        for i in self.items:
            item_details = self.items[i]
            product = item_details['product']          
            if product.seller.sellerId == seller_id:             
                item_id = product.itemId
                if verbose:
                    print(f"Found the seller id {product.seller.sellerId}")
                    print(f"Item ID: {item_id}")
                    print(f"Name: {product.name}")
                    print(f"Price: ${product.price}")
                    print(f"Category: {product.category}")
                    print(f"Quantity: {product.quantity}")
                    print(f"Description: {product.description}")
                    print(f"Seller ID: {seller_id}")
                    print(f"Seller Name: {product.seller.sellerName}")
                    print(f"Seller Address: {product.seller.sellerAddress}")
                    print(f"Rating: {product.rating}")
                    print()
                product = proto.Product(
                    itemId=item_id,
                    name=product.name,
                    price=product.price,
                    category=product.category,
                    quantity=product.quantity,
                    description=product.description,
                    seller=proto.SellerInfo(
                        sellerId=seller_id,
                        sellerName=product.seller.sellerName,
                        sellerAddress=product.seller.sellerAddress
                    ),
                    rating=product.rating
                )
                yield product
            else:
                print('ID not found')
                return iter([])  # Return an empty iterator if the seller has no items

    def SellItem(self, request, context):
        try:
            # Implement logic for selling an item
            product = request.product
            # Check if the seller is registered
            seller_address = product.seller.sellerAddress
            if seller_address not in self.sellers:
                return proto.Response(message="FAIL: Seller not registered.")
            # Assign a unique item ID (placeholder, you might want to use a counter or UUID)
            item_id = str(len(self.items) + 1)
            # print("Here 1")
            # Store the item information
            self.items[item_id] = {
                'id': item_id,
                'product': product,
                'seller_address': seller_address
            }
            
            print(f"Market prints: Sell Item request from {seller_address}")
            print(f"SUCCESS: Item added with ID {item_id}")
            return proto.Response(message=f"SUCCESS")
          

        except Exception as e:
            print(f"Market prints: Error in Sell Item request - {str(e)}")
            return proto.Response(message="FAIL: An error occurred while processing the request.")

    def DeleteItem(self, request, context):
        item_id = request.itemId
        seller_id = request.seller.sellerId
        print(f'Market : Delete Item {item_id} request from {request.seller.sellerAddress}')

        # Check if the item exists
        if item_id in self.items:
            item_details = self.items[item_id]
            product = item_details['product']
            
            # Check if the seller owns the product
            if product.seller.sellerId == seller_id:
                # Delete the item
                del self.items[item_id]
                return proto.Response(message="SUCCESS: Item deleted")
            else:
                return proto.Response(message="FAIL: Seller doesn't own the product")
        else:
            return proto.Response(message="FAIL: Item not found")

    def SearchItem(self, request, context):
        item_name = request.product.name
        category = request.product.category
   
        matching_items = []
        
        for item_id, item_details in self.items.items():
            product = item_details['product']
            if (not item_name or item_name.lower() in product.name.lower()) and \
                    (category == product.category or category == proto.Product.Category.ANY):
                matching_items.append(product)

        print(f"Market prints: Search request for Item name: {item_name}, Category: {category}.")
        for item in matching_items:
            yield item

    def RateItem(self, request, context):
        try:
            product = request.product
            rating = request.rating
            buyer_address = request.buyerAddress

            # Retrieve the product from self.items based on itemId
            if product.itemId in self.items:
                # Update the rating field of the product
                self.items[product.itemId]['product'].rating = float(rating)
                print(f"[Market] : Rating request for item {product.itemId} from {buyer_address}: {rating}")
                return proto.Response(message="SUCCESS: Item rated successfully")
            else:
                return proto.Response(message="FAIL: Item not found")

        except Exception as e:
            print(f"Market prints: Error in rating item - {str(e)}")
            return proto.Response(message="FAIL: An error occurred while rating the item.")

    def AddToWishList(self, request, context):
        product = request.product
        buyer_address = request.buyerAddress

        # Check if the buyer's wishlist exists, if not, create one
        if buyer_address not in self.wishlist:
            self.wishlist[buyer_address] = []

        # Add the product to the buyer's wishlist
        self.wishlist[buyer_address].append(product)

        print(f"[Market]: Added item {product.itemId} to wishlist for {buyer_address}")
        return proto.Response(message="SUCCESS")
    
    def BuyItem(self, request, context):
        order = request.order
        buyer_address = order.buyerAddress
        
        try:
            # Validate the order and process the purchase
            total_price = 0

            for product in order.products:
                # Check if the product exists
                if product.itemId not in self.items:
                    return proto.Response(message=f"FAIL: Item with ID {product.itemId} not found")
                item_details = self.items[product.itemId]
                stored_product = item_details['product']
                
                # Check if the requested quantity is available
                if product.quantity > stored_product.quantity:
                    return proto.Response(message=f"FAIL: Insufficient quantity for item {product.itemId}")
                
                # Calculate the total price
                total_price += product.price * product.quantity
            # Deduct the items' quantities and update the seller's revenue
            for product in order.products:
                item_details = self.items[product.itemId]
                stored_product = item_details['product']
                stored_product.quantity -= product.quantity
                seller_address = item_details['seller_address']
                seller_info = self.sellers[seller_address]['info']
                # seller_info.revenue += product.price * product.quantity

            # Notify the seller about the purchase
            # seller_id = order.seller.sellerId
            # seller_info = self.sellers.get(seller_id)
            # if seller_info:
                # Send a notification to the seller
                # notify_request = proto.NotifyClientRequest(product=order.products[0])
                # seller_stub = create_stub_for_seller(seller_info['info'].sellerAddress)
                # seller_stub.NotifyClient(notify_request)
            
            # Send a confirmation response to the buyer
            return proto.Response(message=f"SUCCESS: Purchase successful. Total price: ${total_price}")
            
        except Exception as e:
            return proto.Response(message=f"FAIL: An error occurred while processing the purchase - {str(e)}")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    proto_grpc.add_MarketServiceServicer_to_server(MarketService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
