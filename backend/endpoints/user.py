from fastapi import APIRouter, Request
from database.database import find_one_collection, add_to_collection, update_to_collection, delete_from_collection, init_pymongo, open_collection, close_client
from misc.misc import read_json, format_error_msg, format_success_msg
from pymongo import MongoClient
import hashlib
import random
import string
import asyncio

router = APIRouter()

@router.post("/login")
async def loginRequest(request: Request):
    email, password, error = await read_json(request, ["email", "password"])
    if error:
        return format_error_msg(error)
    
    return login(email, password)

def login(email, password):
    res = find_one_collection({"email": email, "password": password}, "users")
    if res == None:
        print("Password doesnt match or no user found")
        return format_error_msg("Password doesnt match or no user found")
    else:
        print("Login Successful")
        return format_success_msg({"access": True})

@router.post("/register")
async def registerRequest(request: Request):
    email, name, photo, description, dateIDs, matches, password, error = await read_json(request, 
        [
        "email", "name", "photo", "description", "dateIDs", "matches", "password", 
        ]
        )
    if error:
        return format_error_msg(error)
    res = register(email, name, photo, description, dateIDs, matches, password)
    return res

def register(email, name, photo, description, dateIDs, matches, password):
    usr_jsn =  {"email": email,
                "name": name,
                "photo": photo,
                "description": description,
                "dateIDs": [],
                "matches": [],
                "password": password,
                "pendingMatches": [],
                "pubkey": "dummy1",
                }
    
    res = find_one_collection({"email": email}, "users")

    if res == None:
        usr = add_to_collection(usr_jsn, "users")
        return format_success_msg({"access": True})
    else:
        return format_error_msg("Username exists in a collection, Please try a different one")

@router.post("/getProfile")
async def registerRequest(request: Request):
    email, error = await read_json(request, 
        [
        "email"
        ]
        )
    if error:
        return format_error_msg(error)
    res = getProfile(email)
                
    return res

def getProfile(email):
    res = find_one_collection({"email": email}, "users")

    if res != None:
        print(res)
        return format_success_msg({"profile": res})
    else:
        return format_error_msg("No user found with this email")

# @router.post("/getDates")
# async def getDatesRequest(request: Request):
#     email, error = await read_json(request, ["email"])
#     if error:
#         return format_error_msg(error)
#     res = getDates(email)
#     return res

# # TODO format the date_object 
# def getDates(email):
#     res = find_one_collection({"email": email}, "users")
#     if res == None:
#         print("Not a valid user")
#         return format_error_msg("Not a valid user")
#     else:
#         print(res)
#         dateIds = res["dateIDs"]
        
#         for dateID in dateIds:
#             date_object = find_one_collection({"date"})
#             pass

        # return format_success_msg()

@router.post("/getRandomProfile")
async def getRandomProfileRequest(request: Request):
    email, error = await read_json(["email"])
    if error:
        return format_error_msg(error)
    res = getRandomProfile(email)
    return res

def getRandomProfile(email):
    client = init_pymongo()
    col = open_collection("users", client)
    
    # Get a random profile
    random_doc = col.aggregate([
        {'$sample': {'size': 2}}
    ])

    for doc in random_doc:
        # If the email is itself -> go next
        if(doc['email'] == email):
            continue
        doc['_id'] = str(doc['_id'])
        res = {
            "email": doc["email"],
            "name": doc["name"],
            "description": doc["description"]
        }
        close_client(client)
        print(res)
        return res
    
    close_client(client)
    return {}



@router.post("/acceptMatch")
async def postSendInvitationRequest(request: Request):
    emailUser, emailMatch, error = await read_json(request, 
        ["emailUser", 
         "emailMatch"])
    if error:
        return format_error_msg(error)
    res = acceptMatch(emailUser, emailMatch)
    if (res["success"] == False):
        return res
    return format_success_msg(res)

# emailUser (A)
# emailMatch (B)
def acceptMatch(emailUser, emailMatch):
    userProfile = find_one_collection({"email": emailUser}, "users")

    if userProfile == None:
        return format_error_msg("Email user does not exists")

    pendingMatches = userProfile["pendingMatches"]

    # Case 2: Already in pending matches
    for match in pendingMatches:
        if match == emailMatch:
            print("case 2")
            pendingMatches.remove(emailMatch)
            update_to_collection({"email": emailUser}, {"pendingMatches": pendingMatches}, "users")

            matchProfile = find_one_collection({"email": emailMatch}, "users")
            if matchProfile == None:
                return format_error_msg("Email match does not exists")
            aexists = addToMatchedPeopleArrayA(emailUser, emailMatch)
            bexists = addToMatchedPeopleArrayA(emailMatch, emailUser)
            return {"access": True}
        
    # Case 1: Not in pending match -> add to emailMatch
    print("case 1")
    matchProfile = find_one_collection({"email": emailMatch}, "users")
    if matchProfile == None:
        return format_error_msg("Email match does not exists")
    
    print(matchProfile)

    pendingMatchesB = matchProfile["pendingMatches"]
    pendingMatchesB.append(emailUser)
    update_to_collection({"email": emailMatch}, {"pendingMatches": pendingMatchesB}, "users")
    return {"access": True}

def addToMatchedPeopleArrayA(emailA, emailB):
    aProfile = find_one_collection({"email": emailA}, "users")
    if aProfile == None:
        return False
    matchedPeopleArrayA = aProfile["matches"]
    matchedPeopleArrayA.append(emailB)
    update_to_collection({"email": emailA}, {"matches": matchedPeopleArrayA}, "users")
    return True
    

# @router.post("/getPendingMatches")
# async def getPendingMatchesRequest(request: Request):
#     emailUser, error = await read_json(re)
    

# print("Register 1")
# register("1", "2", "3", "4", "5", "6", "7")
# print("Register 123")
# register("abc@mail.com", "2", "3", "4", "5", "6", "7")
# print("Accepting match")
# acceptMatch("1", "123")
# acceptMatch("123", "1")

# login("1", "6")
# getProfile("2")
# getDates("1")

# print(acceptMatch("1234@m.com", "123"))
# print(acceptMatch("123", "1234@m.com"))