# # buyer.py
# # to compile protofile : protoc --proto_path=. --python_out=. ./market.proto
# # python -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. market.proto
# import grpc
# import market_pb2 as proto
# import market_pb2_grpc as proto_grpc
# import logging
# import uuid
# import threading

# logging.basicConfig(level=logging.INFO)

# def create_stub():
#     return proto_grpc.MarketServiceStub(grpc.insecure_channel('localhost:50051'))


# def search_item(item_name='', category='ANY'):
#     try:
#         stub = create_stub()  
#         product = proto.Product(name=item_name, category=category)
#         request = proto.SearchItemRequest(product=product)
#         responses = stub.SearchItem(request)
#         print(f"Market prints: Search request for Item name: {item_name}, Category: {category}")
#         count = 0
#         for response in responses:
#             count+=1
#             print("-"*50,"\n",count)
#             print(response)
#     except grpc.RpcError as e:
#         logging.error(f"Error in gRPC call: {e}")

# def buy_item(item_id, quantity, buyer_address):
#     try:
#         stub = create_stub()
#         order = proto.Order(
#             orderId=str(uuid.uuid4()),
#             seller=proto.SellerInfo(sellerId='', sellerName='', sellerAddress=''),  # Fill in seller information
#             buyerAddress=buyer_address,
#             products=[proto.Product(itemId=item_id, name='', price=0.0, category='', quantity=quantity, description='', seller=proto.SellerInfo(sellerId='', sellerName='', sellerAddress=''), rating=0.0)]
#         )
#         response = stub.BuyItem(order)
#         print(f"Market prints: Buy request {quantity} of item {item_id}, from {buyer_address}")
#         print(f"Buyer prints: {response.message}")
#         # Send notification to seller
#         notification_request = proto.NotifyClientRequest(product=proto.Product(itemId=item_id))
#         # notification_response = stub.NotifyClient(notification_request)
#         print("Notification sent to seller.")
#     except grpc.RpcError as e:
#         logging.error(f"Error in gRPC call: {e}")

# def add_to_wishlist(item_id, buyer_address):
#     try:
#         stub = create_stub()
#         request = proto.AddToWishListRequest(product=proto.Product(itemId=item_id), buyerAddress=buyer_address)
#         response = stub.AddToWishList(request)
#         print(f"[Market] : Wishlist request of item {item_id}, from {buyer_address}")
#         print(f"[Buyer] : {response.message}")
#     except grpc.RpcError as e:
#         logging.error(f"Error in gRPC call: {e}")

# def rate_item(item_id, rating, buyer_address):
#     try:
#         stub = create_stub()
#         request = proto.RateItemRequest(
#             product=proto.Product(itemId=item_id),
#             rating=str(rating),
#             buyerAddress=buyer_address  # Use buyerAddress instead of buyer_address
#         )
#         response = stub.RateItem(request)
#         print(f"Market prints: {buyer_address} rated item {item_id} with {rating} stars.")
#         print(f"Buyer prints: {response.message}")
#     except grpc.RpcError as e:
#         logging.error(f"Error in gRPC call: {e}")


# def main_menu():
#     while True:
#         print("\n=== BUYER MENU ===")
#         print("1. Search Item")
#         print("2. Buy Item")
#         print("3. Add to Wishlist")
#         print("4. Rate Item")
#         print("5. Exit")
#         choice = input("Enter your choice: ")
#         if choice == '1':
#             item_name = input("Enter item name to search: ")
#             category = input("Enter item category to search (ELECTRONICS, FASHION, OTHERS): ")
#             search_item(item_name, category)
#         elif choice == '2':
#             item_id = input("Enter item ID to buy: ")
#             quantity = int(input("Enter quantity to buy: "))
#             buyer_address = input("Enter buyer address: ")
#             buy_item(item_id, quantity, buyer_address)
#         elif choice == '3':
#             item_id = input("Enter item ID to add to wishlist: ")
#             buyer_address = input("Enter buyer address: ")
#             add_to_wishlist(item_id, buyer_address)
#         elif choice == '4':
#             item_id = input("Enter item ID to rate: ")
#             rating = int(input("Enter rating (1-5): "))
#             buyer_address = input("Enter buyer address: ")
#             rate_item(item_id, rating, buyer_address)
#         elif choice == '5':
#             break
#         else:
#             print("Invalid choice. Please try again.")

# # Example usage
# if __name__ == '__main__':
#     # search_item("Product3",'OTHERS')
#     # search_item()
#     # buy_item('1', 1, 'buyer_address')
#     # add_to_wishlist('2', 'buyer_address')
#     # rate_item('2', 4, 'buyer_address')

#     # Start a thread to receive notifications
#     # notification_thread = threading.Thread(target=receive_notifications)
#     # notification_thread.start()
#     main_menu()


import grpc
import market_pb2 as proto
import market_pb2_grpc as proto_grpc
import logging
import uuid
import threading

logging.basicConfig(level=logging.INFO)

class Buyer:
    def __init__(self, buyer_address):
        self.buyer_address = buyer_address
        self.stub = proto_grpc.MarketServiceStub(grpc.insecure_channel('localhost:50051'))

    def search_item(self, item_name='', category='ANY'):
        try:
            product = proto.Product(name=item_name, category=category)
            request = proto.SearchItemRequest(product=product)
            responses = self.stub.SearchItem(request)
            print(f"Market prints: Search request for Item name: {item_name}, Category: {category}")
            count = 0
            for response in responses:
                count+=1
                print("-"*50,"\n",count)
                print(response)
        except grpc.RpcError as e:
            logging.error(f"Error in gRPC call: {e}")

    def buy_item(self, item_id, quantity):
        try:
            order = proto.Order(
                orderId=str(uuid.uuid4()),
                seller=proto.SellerInfo(sellerId='your_seller_id_here', sellerName='SellerName', sellerAddress='192.13.188.178:50051'),
                buyerAddress='buyer_address_here',
                products=[proto.Product(itemId=item_id, name='Item Name', price=10.0, category=proto.Product.Category.OTHERS, quantity=quantity, description='Description', seller=proto.SellerInfo(sellerId='your_seller_id_here', sellerName='SellerName', sellerAddress='192.13.188.178:50051'), rating=0.0)]
            )
            response = self.stub.BuyItem(proto.BuyItemRequest(order=order))

            # order = proto.Order(
            #     orderId=str(uuid.uuid4()),
            #     seller=proto.SellerInfo(sellerId='', sellerName='', sellerAddress=''),  # Fill in seller information
            #     buyerAddress=self.buyer_address,
            #     products=[proto.Product(itemId=item_id, name='', price=0.0, category='OTHERS', quantity=quantity, description='', seller=proto.SellerInfo(sellerId='', sellerName='', sellerAddress=''), rating=0.0)]
            # )
            # response = self.stub.BuyItem(order)
            print(f"Market prints: Buy request {quantity} of item {item_id}, from {self.buyer_address}")
            print(f"Buyer prints: {response.message}")
            # Send notification to seller
            # notification_request = proto.NotifyClientRequest(product=proto.Product(itemId=item_id))
            # notification_response = self.stub.NotifyClient(notification_request)
            print("Notification sent to seller.")
        except grpc.RpcError as e:
            logging.error(f"Error in gRPC call: {e}")

    def add_to_wishlist(self, item_id):
        try:
            request = proto.AddToWishListRequest(product=proto.Product(itemId=item_id), buyerAddress=self.buyer_address)
            response = self.stub.AddToWishList(request)
            print(f"[Market] : Wishlist request of item {item_id}, from {self.buyer_address}")
            print(f"[Buyer] : {response.message}")
        except grpc.RpcError as e:
            logging.error(f"Error in gRPC call: {e}")

    def rate_item(self, item_id, rating):
        try:
            request = proto.RateItemRequest(
                product=proto.Product(itemId=item_id),
                rating=str(rating),
                buyerAddress=self.buyer_address
            )
            response = self.stub.RateItem(request)
            print(f"Market prints: {self.buyer_address} rated item {item_id} with {rating} stars.")
            print(f"Buyer prints: {response.message}")
        except grpc.RpcError as e:
            logging.error(f"Error in gRPC call: {e}")

    def main_menu(self):
        while True:
            print("\n=== BUYER MENU ===")
            print("1. Search Item")
            print("2. Buy Item")
            print("3. Add to Wishlist")
            print("4. Rate Item")
            print("5. Exit")
            choice = input("Enter your choice: ")
            if choice == '1':
                item_name = input("Enter item name to search: ")
                category = input("Enter item category to search (ELECTRONICS, FASHION, OTHERS): ")
                self.search_item(item_name, category)
            elif choice == '2':
                item_id = input("Enter item ID to buy: ")
                quantity = int(input("Enter quantity to buy: "))
                self.buy_item(item_id, quantity)
            elif choice == '3':
                item_id = input("Enter item ID to add to wishlist: ")
                self.add_to_wishlist(item_id)
            elif choice == '4':
                item_id = input("Enter item ID to rate: ")
                rating = int(input("Enter rating (1-5): "))
                self.rate_item(item_id, rating)
            elif choice == '5':
                break
            else:
                print("Invalid choice. Please try again.")

if __name__ == '__main__':
    buyer_address = input("Enter buyer address: ")
    buyer = Buyer(buyer_address)
    buyer.main_menu()
