# # seller.py
# # to compile protofile : protoc --proto_path=. --python_out=. ./market.proto
# # python -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. market.proto
# import grpc
# import market_pb2 as proto
# import market_pb2_grpc as proto_grpc
# import uuid
# import logging
# import time
# import threading

# logging.basicConfig(level=logging.INFO)

# def create_stub():
#     return proto_grpc.MarketServiceStub(grpc.insecure_channel('localhost:50051'))

# def register_seller():
#     try:
#         stub = create_stub()
#         seller_info = proto.SellerInfo(
#             # sellerId=str(uuid.uuid4()),  # Use uuid4 for random UUID
#             sellerId = '0ec0eb05-e0c8-4073-9bf2-cadaa32cb220',
#             sellerName='SellerName',
#             sellerAddress='192.13.188.178:50051'
#         )
#         request = proto.RegisterSellerRequest(sellerInfo=seller_info)
#         response = stub.RegisterSeller(request)
#         logging.info(f"Market prints: Seller join request from {seller_info.sellerAddress}, uuid = {seller_info.sellerId}")
#         logging.info(f"Seller prints: {response.message}")
#     except grpc.RpcError as e:
#         logging.error(f"Error in gRPC call: {e}")

# def sell_item(in_name,in_price,in_category,in_quantity,in_rating,in_description = 'Description of Product'):
#     try:
#         stub = create_stub()
#         # seller_id = str(uuid.uuid4())  # Use uuid4 for random UUID
#         seller_id = '0ec0eb05-e0c8-4073-9bf2-cadaa32cb220'
#         seller_address = '192.13.188.178:50051'
#         product = proto.Product(
#             itemId=str(uuid.uuid4()),  # Use uuid4 for random UUID
#             name=in_name,
#             price=in_price,
#             category=proto.Product.Category.Value(in_category),  # Replace 'ELECTRONICS' with the actual category value
#             quantity=in_quantity,
#             description=in_description,
#             seller=proto.SellerInfo(sellerId=seller_id, sellerName='SellerName', sellerAddress=seller_address),
#             rating=in_rating
#         )
#         request = proto.SellItemRequest(product=product)
#         response = stub.SellItem(request)
#         if response.message == "SUCCESS":
#             logging.info(f"Market prints: Sell Item request from {product.seller.sellerAddress}")
#             logging.info(f"Seller prints: SUCCESS, Item ID: {product.itemId}")
#         else:
#             logging.info(f"Seller prints: FAIL")
#     except grpc.RpcError as e:
#         logging.error(f"Error in gRPC call: {e}")

# def update_item(item_id, new_price, new_quantity, seller_address, seller_id):
#     try:
#         stub = create_stub()
#         request = proto.UpdateItemRequest(
#             itemId=item_id,
#             newPrice=new_price,
#             newQuantity=new_quantity,
#             seller=proto.SellerInfo(sellerId=seller_id, sellerAddress=seller_address)
#         )
#         response = stub.UpdateItem(request)
#         if response.message == "SUCCESS":
#             logging.info(f"Market prints: Update Item {item_id} request from {seller_address}")
#             logging.info(f"Seller prints: SUCCESS")
#         else:
#             logging.info(f"Seller prints: FAIL")
#     except grpc.RpcError as e:
#         logging.error(f"Error in gRPC call: {e}")

# def delete_item(item_id, seller_address, seller_id):
#     try:
#         stub = create_stub()
#         request = proto.DeleteItemRequest(itemId=item_id, seller=proto.SellerInfo(sellerId=seller_id, sellerAddress=seller_address))
#         response = stub.DeleteItem(request)
        
#         if response.message == "SUCCESS":
#             logging.info(f"Market prints: Delete Item {item_id} request from {seller_address}")
#             logging.info(f"Seller prints: SUCCESS")
#         else:
#             logging.info(f"Seller prints: FAIL - {response.message}")
            
#     except grpc.RpcError as e:
#         # Handle gRPC errors
#         logging.error(f"Error in gRPC call: {e.details()} (code: {e.code()})")

# def display_seller_items(seller_address, seller_id):
#     try:
#         stub = create_stub()
#         request = proto.DisplaySellerItemsRequest(sellerInfo=proto.SellerInfo(sellerId=seller_id, sellerAddress=seller_address))
   
#         response_iterator = stub.DisplaySellerItems(request)
#         logging.info(f"Market prints: Display Items request from {seller_address}")
#         count = 0
#         for product in response_iterator:
#             count+=1
#             print("-"*50,"\n",count)
#             logging.info(f"Item ID: {product.itemId}, Price: ${product.price}, Name: {product.name}, Category: {proto.Product.Category.Name(product.category)}")
#             logging.info(f"Description: {product.description}")
#             logging.info(f"Quantity Remaining: {product.quantity}")
#             logging.info(f"Seller: {product.seller.sellerAddress}")
#             logging.info(f"Rating: {product.rating} / 5")
#             logging.info("\n")
#         logging.info(f"Market prints: Display Items request from {seller_address} completed.")
#     except Exception as e:
#         logging.error(f"Error in displaying seller items: {e}")

# def main_menu():
#     while True:
#         print("\n=== SELLER MENU ===")
#         print("1. Register as Seller")
#         print("2. Sell Item")
#         print("3. Update Item")
#         print("4. Delete Item")
#         print("5. Display Seller Items")
#         print("6. Exit")
#         choice = input("Enter your choice: ")
#         if choice == '1':
#             register_seller()
#         elif choice == '2':
#             name = input("Enter item name: ")
#             price = float(input("Enter item price: "))
#             category = input("Enter item category (ELECTRONICS, FASHION, OTHERS): ")
#             quantity = int(input("Enter item quantity: "))
#             rating = float(input("Enter item rating: "))
#             sell_item(name, price, category, quantity, rating)
#         elif choice == '3':
#             item_id = input("Enter item ID to update: ")
#             new_price = float(input("Enter new price: "))
#             new_quantity = int(input("Enter new quantity: "))
#             update_item(item_id=item_id, new_price=new_price, new_quantity=new_quantity, seller_address='192.13.188.178:50051', seller_id='0ec0eb05-e0c8-4073-9bf2-cadaa32cb220')
#             # update_item(item_id, new_price, new_quantity)
#         elif choice == '4':
#             item_id = input("Enter item ID to delete: ")
#             delete_item(item_id, seller_address='192.13.188.178:50051', seller_id='0ec0eb05-e0c8-4073-9bf2-cadaa32cb220')
#         elif choice == '5':
#             # display_seller_items()
#             display_seller_items(seller_address='192.13.188.178:50051', seller_id='0ec0eb05-e0c8-4073-9bf2-cadaa32cb220')
#         elif choice == '6':
#             break
#         else:
#             print("Invalid choice. Please try again.")

# if __name__ == '__main__':
#     # register_seller()
#     # sell_item("Product1", 10.0, "ELECTRONICS", 10, 4.5)
#     # time.sleep(1)
#     # sell_item("Product2", 20.0, "FASHION", 20, 4.0)
#     # time.sleep(1)
#     # sell_item("Product3", 15.0, "OTHERS", 15, 4.2)
#     # time.sleep(1)
#     # sell_item("Product4", 25.0, "ELECTRONICS", 5, 4.8)
#     # time.sleep(1)
#     # sell_item("Product5", 12.0, "FASHION", 30, 4.6)
#     # time.sleep(1)
#     # sell_item("Product6", 18.0, "OTHERS", 8, 3.9)
#     # time.sleep(1)
#     # sell_item("Product7", 30.0, "ELECTRONICS", 12, 4.1)
#     # time.sleep(1)
#     # sell_item("Product8", 22.0, "FASHION", 25, 4.4)
#     # time.sleep(1)
#     # sell_item("Product9", 17.0, "OTHERS", 20, 4.3)
#     # time.sleep(1)
#     # sell_item("Product10", 35.0, "ELECTRONICS", 18, 4.7)
#     # time.sleep(1)

#     # update_item(item_id='1', new_price=20.0, new_quantity=5, seller_address='192.13.188.178:50051', seller_id='0ec0eb05-e0c8-4073-9bf2-cadaa32cb220')
#     # display_seller_items(seller_address='192.13.188.178:50051', seller_id='0ec0eb05-e0c8-4073-9bf2-cadaa32cb220')

#     # delete_item(item_id='1', seller_address='192.13.188.178:50051', seller_id='0ec0eb05-e0c8-4073-9bf2-cadaa32cb220')
#     # display_seller_items(seller_address='192.13.188.178:50051', seller_id='0ec0eb05-e0c8-4073-9bf2-cadaa32cb220')

#     # # Start a new thread to receive notifications
#     # notification_thread = threading.Thread(target=receive_notifications)
#     # notification_thread.start()

#     # register_seller()
#     # notification_thread = threading.Thread(target=receive_notifications)
#     # notification_thread.start()
#     main_menu()

import grpc
import market_pb2 as proto
import market_pb2_grpc as proto_grpc
import uuid
import logging
import time
import threading

logging.basicConfig(level=logging.INFO)

class Seller:
    def __init__(self, seller_id, seller_name, seller_address):
        self.seller_id = seller_id
        self.seller_name = seller_name
        self.seller_address = seller_address
        self.stub = proto_grpc.MarketServiceStub(grpc.insecure_channel('localhost:50051'))

    def register_seller(self):
        try:
            seller_info = proto.SellerInfo(
                sellerId=self.seller_id,
                sellerName=self.seller_name,
                sellerAddress=self.seller_address
            )
            request = proto.RegisterSellerRequest(sellerInfo=seller_info)
            response = self.stub.RegisterSeller(request)
            logging.info(f"Market prints: Seller join request from {self.seller_address}, uuid = {self.seller_id}")
            logging.info(f"Seller prints: {response.message}")
        except grpc.RpcError as e:
            logging.error(f"Error in gRPC call: {e}")

    def sell_item(self, name, price, category, quantity, rating, description='Description of Product'):
        try:
            product = proto.Product(
                itemId=str(uuid.uuid4()),
                name=name,
                price=price,
                category=proto.Product.Category.Value(category),
                quantity=quantity,
                description=description,
                seller=proto.SellerInfo(sellerId=self.seller_id, sellerName=self.seller_name, sellerAddress=self.seller_address),
                rating=rating
            )
            request = proto.SellItemRequest(product=product)
            response = self.stub.SellItem(request)
            if response.message == "SUCCESS":
                logging.info(f"Market prints: Sell Item request from {self.seller_address}")
                logging.info(f"Seller prints: SUCCESS, Item ID: {product.itemId}")
            else:
                logging.info(f"Seller prints: FAIL")
        except grpc.RpcError as e:
            logging.error(f"Error in gRPC call: {e}")

    def update_item(self, item_id, new_price, new_quantity):
        try:
            request = proto.UpdateItemRequest(
                itemId=item_id,
                newPrice=new_price,
                newQuantity=new_quantity,
                seller=proto.SellerInfo(sellerId=self.seller_id, sellerAddress=self.seller_address)
            )
            response = self.stub.UpdateItem(request)
            if response.message == "SUCCESS":
                logging.info(f"Market prints: Update Item {item_id} request from {self.seller_address}")
                logging.info(f"Seller prints: SUCCESS")
            else:
                logging.info(f"Seller prints: FAIL")
        except grpc.RpcError as e:
            logging.error(f"Error in gRPC call: {e}")

    def delete_item(self, item_id):
        try:
            request = proto.DeleteItemRequest(itemId=item_id, seller=proto.SellerInfo(sellerId=self.seller_id, sellerAddress=self.seller_address))
            response = self.stub.DeleteItem(request)
            
            if response.message == "SUCCESS":
                logging.info(f"Market prints: Delete Item {item_id} request from {self.seller_address}")
                logging.info(f"Seller prints: SUCCESS")
            else:
                logging.info(f"Seller prints: FAIL - {response.message}")
                
        except grpc.RpcError as e:
            logging.error(f"Error in gRPC call: {e}")

    def display_items(self):
        try:
            request = proto.DisplaySellerItemsRequest(sellerInfo=proto.SellerInfo(sellerId=self.seller_id, sellerAddress=self.seller_address))
       
            response_iterator = self.stub.DisplaySellerItems(request)
            logging.info(f"Market prints: Display Items request from {self.seller_address}")
            count = 0
            for product in response_iterator:
                count+=1
                print("-"*50,"\n",count)
                logging.info(f"Item ID: {product.itemId}, Price: ${product.price}, Name: {product.name}, Category: {proto.Product.Category.Name(product.category)}")
                logging.info(f"Description: {product.description}")
                logging.info(f"Quantity Remaining: {product.quantity}")
                logging.info(f"Seller: {product.seller.sellerAddress}")
                logging.info(f"Rating: {product.rating} / 5")
                logging.info("\n")
            logging.info(f"Market prints: Display Items request from {self.seller_address} completed.")
        except Exception as e:
            logging.error(f"Error in displaying seller items: {e}")

    def main_menu(self):
        while True:
            print("\n=== SELLER MENU ===")
            print("1. Register as Seller")
            print("2. Sell Item")
            print("3. Update Item")
            print("4. Delete Item")
            print("5. Display Seller Items")
            print("6. Exit")
            choice = input("Enter your choice: ")
            if choice == '1':
                self.register_seller()
            elif choice == '2':
                name = input("Enter item name: ")
                price = float(input("Enter item price: "))
                category = input("Enter item category (ELECTRONICS, FASHION, OTHERS): ")
                quantity = int(input("Enter item quantity: "))
                rating = float(input("Enter item rating: "))
                self.sell_item(name, price, category, quantity, rating)
            elif choice == '3':
                item_id = input("Enter item ID to update: ")
                new_price = float(input("Enter new price: "))
                new_quantity = int(input("Enter new quantity: "))
                self.update_item(item_id, new_price, new_quantity)
            elif choice == '4':
                item_id = input("Enter item ID to delete: ")
                self.delete_item(item_id)
            elif choice == '5':
                self.display_items()
            elif choice == '6':
                break
            else:
                print("Invalid choice. Please try again.")

if __name__ == '__main__':
    seller_id = str(uuid.uuid4())
    seller_name = 'Seller1'
    seller_address = '192.13.188.178:50051'
    seller = Seller(seller_id, seller_name, seller_address)
    seller.main_menu()
