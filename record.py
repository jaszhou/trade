trade_record = {
#   "BTCUST": 2,
#   "BNBUST": 1,
}


def add_trade(pair):
    
    if trade_record.get(pair):
        print("record exists")
        trade_record[pair] += 1
    else:
        # print("record does not exist, add record")
        trade_record[pair] = 1

    print(trade_record)

def get_trade(pair):

    count = 0

    if trade_record.get(pair):
        
        count = trade_record[pair]
        print(f"record count {count}")
    # else:
    #     print("record does not exist")
       
    return count


# add_trade("BTCUST")
# add_trade("ETHUST")
# get_trade("BTCUST")