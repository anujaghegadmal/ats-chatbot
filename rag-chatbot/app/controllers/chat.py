from app.services.model_inference import query_profiles, generate_detailed_response

class ChatController:
# (request.role, request.message)
    async def process_user_message(self, user_query: str):
        print("hit in chat controller",user_query)
        
        # Query profiles based on user query
        response_query_profiles = await query_profiles(user_query)
        
        # Call generate_detailed_response with both the query and profiles
        result = await generate_detailed_response(user_query, response_query_profiles)
        
        print("result from controller =>",result)
        return result
    