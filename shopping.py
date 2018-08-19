import os
from flask import Flask, request, render_template, redirect, flash, session
from pymongo import MongoClient

MONGODB_URI = os.environ.get("MONGODB_URI")
MONGODB_NAME = os.environ.get("MONGODB_NAME")

app = Flask(__name__)
app.secret_key = "secretKeyHere"

@app.route('/')
def get_index():
    return render_template('index.html')
    
@app.route("/login", methods=['POST'])
def do_login():
    username = request.form['username']
    return redirect(username)
    
@app.route("/<username>") 
def get_userpage(username):
    documents = load_documents(username)
    return render_template("user_home.html", username=username, documents=documents)

@app.route("/<username>/create_new_list", methods=["POST"]) 
def create_list(username):
    list_name= request.form['list_name']
    create_list_for_user(username,list_name)
    return redirect(username)
    
@app.route("/<username>/<list_name>/add_item", methods=["POST"]) 
def add_item_to_list(username, list_name):
    if(request.form.getlist('priority') != None):
        priority = 1
    else:
        priority = 0

    item_name = request.form['item_name']
    quantity = int(request.form['quantity'])
    list_item= {'name': item_name, 'priority': priority, 'quantity': quantity}
    save_list_items_to_mongo(username, list_name, list_item)
    msgString = 'Item "%s", added to "%s" list !'%(item_name,list_name)
    flash(msgString)
    return redirect(username)
    
@app.route('/<username>/<list_name>/<item_name>/delete_item',methods=['POST'])
def delete_item(username, list_name, item_name):
    with MongoClient(MONGODB_URI) as conn:
        db = conn[MONGODB_NAME]
        selected_list = db[username].find_one({'name':list_name})
        #selected_list['list_items'].remove({'name': item_name})
        selected_list['list_items'] = removeObjFromList(selected_list['list_items'], item_name)
        
        db[username].save(selected_list)
        msgString = 'Item "%s", removed from "%s" list !'%(item_name, selected_list['name'])
        flash(msgString)
        
        return redirect(username)
        
def removeObjFromList(list_items, item_name):
    for counter, item in enumerate(list_items):
        if item['name'] == item_name:
            del(list_items[counter]) 
            break
        
    return list_items
    

# @app.route('/<username>/<list_name>/<create_new_list>/delete_title',methods=['POST'])
# def delete_title(username, list_name, create_new_list):
#     with MongoClient(MONGODB_URI) as conn:
#         db = conn[MONGODB_NAME]
#         selected_list = db[username].find_one({'list':list_name})
#         selected_list['list_items'].remove(create_new_list)
#         db[username].save(selected_list)
#         return redirect(username)
        
@app.route('/<username>/<list_name>/<item_name>/priority_item',methods=['POST'])
def priority_item(username, list_name, item_name):
    with MongoClient(MONGODB_URI) as conn:
        db = conn[MONGODB_NAME]
        selected_list = db[username].find_one({'name':list_name})
        selected_list['list_items'].mark(item_name)
        db[username].save(selected_list)
        return redirect(username)

def create_list_for_user(username, list_name):
    with MongoClient(MONGODB_URI) as conn:
        db = conn[MONGODB_NAME]
        db[username].insert({'name': list_name, 'list_items': [] })
        
# def load_lists_by_username(username):
#     with MongoClient(MONGODB_URI) as conn:
#         db = conn[MONGODB_NAME]
#         return db[username].find()

def save_list_items_to_mongo(username, list_name, new_list_item):
    with MongoClient(MONGODB_URI) as conn:
        db = conn[MONGODB_NAME]
        selected_list = db[username].find_one({'name':list_name})
        selected_list['list_items'].append(new_list_item)
        db[username].save(selected_list)

def load_documents(username):
    with MongoClient(MONGODB_URI) as conn:
        db = conn[MONGODB_NAME]
        list_obj = db[username].find()
        return [l for l in list_obj]
        
        
        
        
        
        
if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)), debug=True)
    
    
    
    