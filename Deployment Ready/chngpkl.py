import pickle

with open('lastorder.pkl', 'rb') as f:
    orderID, side, prevquantity = pickle.load(f)
print("Previous orderID =", orderID, ", side =", side, "and quantity =", prevquantity)

orderID = 'testing'
side = 'SELL'
prevquantity = 0.003

with open('lastorder.pkl', 'wb') as f:
            pickle.dump([orderID, side, prevquantity], f)
print("Previous orderID =", orderID, ", side =", side, "and quantity =", prevquantity)
