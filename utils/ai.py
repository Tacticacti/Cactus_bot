import google.generativeai as genai
import config

def ask_gemini(user_message, username):
    """
    Sends the message to Gemini and returns the response.
    Updated to use Gemini 2.5 Flash.
    """
    if not config.GEMINI_API_KEY:
        return "🧠 **Error:** My brain is missing! (GEMINI_API_KEY not found)"

    try:
        genai.configure(api_key=config.GEMINI_API_KEY)
        
        # UPDATED: Use the model explicitly listed in your logs
        model_name = 'gemini-2.5-flash'
        
        # Define the persona
        # prompt = (
        #     f"You are a helpful Advent of Code elf assistant named AoCBot. "
        #     f"The user '{username}' said: {user_message}. "
        #     f"Keep your answer concise (under 2000 characters) and festive."
        # )
        prompt = (
            f"You are a sharp, tactical cactus assistant named CactusBot. "
            f"The user '{username}' said: {user_message}. "
            f"Your personality is helpful but slightly prickly. Use cactus puns where appropriate (sharp, on point, stuck, needles). "
            f"Keep your answer concise (under 2000 characters) and tactical."
        )
        
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as inner_e:
            # If 2.5 fails, let's try to find ANY valid model dynamically
            print(f"⚠️ Primary model failed: {inner_e}. Searching for backups...")
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    if 'flash' in m.name:
                        print(f"🔄 Switching to backup brain: {m.name}")
                        backup_model = genai.GenerativeModel(m.name)
                        response = backup_model.generate_content(prompt)
                        return response.text
            raise inner_e # Re-raise if no backups found

    except Exception as e:
        print(f"❌ Critical Gemini Error: {e}")
        return "🔥 **My circuits are overheating!** (I couldn't find a valid AI model to talk to.)"