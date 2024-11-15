from flask import Flask, request, jsonify, render_template,session,redirect

import pickle
import joblib
import re 
import google.generativeai as genai
import mysql.connector
from mysql.connector import Error


app = Flask(__name__)
def get_db_connection():
    connection = mysql.connector.connect(
        host='127.0.0.1',  
        port=3306,
        user='root',   # MySQL username
        password='Tn22e3281#',  # MySQL password
        database='carbon'   # Your database name
    )
    return connection

app.secret_key = 'Tn22e3281#'
with open('cf.pkl', 'rb') as file:
    cf = pickle.load(file)
    

with open('model_individual.joblib', 'rb') as f:
    model_individual = joblib.load(f)


with open('model_national.pkl', 'rb') as f:
    model_national = joblib.load(f)

@app.route('/')
def index():
    return render_template('home.html')
    

@app.route('/options')
def options():
    return render_template('options.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/about_our_work')
def about_us():
    return render_template('about_our_work.html')

@app.route('/learn_more')
def learn_more():
    return render_template('learn_more.html')

@app.route('/individualfootprint')
def individualfootprint():
    return render_template('individualsurvey.html')

@app.route('/nationalfootprint')
def nationalfootprint():
    return render_template('nationalsurvey.html')

@app.route('/predict-individual', methods=['POST'])
def predict():
    data = request.get_json()
    
    
    defaults = {
        'Recycling_Glass': False,
        'Recycling_Metal': 0,
        'Recycling_Plastic': 0,
        'Recycling_Paper': 0,
        'Cooking_With_Oven': False,
        'Cooking_With_Microwave': 0,
        'Cooking_With_Grill': 0,
        'Cooking_With_Airfryer': 0,
        'Cooking_With_Stove': 0
    }

   
    data = {**defaults, **data}
    print(data)
    if 'Monthly_' not in data:
        data['Cooking_With_Stove'] = 0 
    user_id = data.get('user_id')
    month = data.get('month')
    input_data = {key: value for key, value in data.items() if key not in ['user_id', 'month']}

    import pandas as pd
    input_data_df = pd.DataFrame(input_data, index=[0])
    # User_id = input_data.iloc[:, 9]

    # print(User_id[0])
    #input_data_df = input_data_df.drop(input_data_df.columns[9], axis=1)  # Adjust based on your input structure

    
    transformed_input = cf.transform(input_data_df)
    
    prediction = model_individual.predict(transformed_input)
    
    GOOGLE_API_KEY = "AIzaSyC_Noz73FQAQxb4VrmW98RhFG81WbWX-2U"
    genai.configure(api_key=GOOGLE_API_KEY)
    genai_model = genai.GenerativeModel('gemini-1.5-flash')
    
   
    para_prompt = (
        "Based on the following data, provide 5 clear and concise suggestions "
        "to reduce carbon footprint. Please number the suggestions:"
    )
    
    input_prompt_str = str(input_data_df.to_dict(orient='records')[0])
    response = genai_model.generate_content(para_prompt + input_prompt_str)
    
    modified_text = re.sub(r'[\*\d]', '', response.text)
    points = modified_text.split('.')
    formatted_text = '\n'.join([point.strip() + '.' for point in points if point.strip()])
    
    print(formatted_text.encode('utf-8').decode('utf-8'))
    
    
    para_prompt2="give me the number of trees i owe to the enviornment based on the following info,just give me like a number, nothing else, no text nothing, just a number:"
    input_prompt_str2 = str(input_data_df.to_dict(orient='records')[0])
    response2 = genai_model.generate_content(para_prompt2 + input_prompt_str2)
    
    footprint = round(float(prediction[0]) / 1000, 2)
    credit = round(float(prediction[0]) / 1000, 2)
    heat = round((float(prediction[0]) / 1000) * 33.4, 2)
    tree = int(response2.text)

    # Insert the data into the database
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        query = """
        INSERT INTO individual (user_id, month, monthly_grocery_bill, vehicle_monthly_distance, waste_bag, tv_pc_hour, 
            new_clothes, internet, material, cooking, body, sex, diet, shower, heating_source, social, travel_air, 
            waste_bag_size, energy, transport, footprint, credits, heat, trees, suggestions)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
        """
        values = (
            user_id, month, 
            data.get('Monthly_Grocery_Bill'), data.get('Vehicle_Monthly_Distance_Km'), data.get('Waste_Bag_Weekly_Count'), 
            data.get('How_Long_TV_PC_Daily_Hour'), data.get('How_Many_New_Clothes_Monthly'), data.get('How_Long_Internet_Daily_Hour'), 
            data.get('Recycling_Materials'),
            data.get('Cooking_Methods'), data.get('Body_Type'), data.get('Sex'), data.get('Diet'), data.get('How_Often_Shower'),
            data.get('Heating_Energy_Source'), data.get('Social_Activity'), data.get('Frequency_of_Traveling_by_Air'), data.get('Waste_Bag_Size'),
            data.get('Energy_efficiency'), data.get('Transport_Vehicle_Type'), footprint, credit, heat, tree, formatted_text
        )

        cursor.execute(query, values)
        connection.commit()  # Save changes to the database
        cursor.close()
        connection.close()

        print("Data inserted successfully.")
    else:
        print("Database connection failed.")
        
    return jsonify({'prediction': prediction[0], 'suggestions': formatted_text,'trees':response2.text})

@app.route('/predictnational', methods=['POST'])
def predictnational():
    data1 = request.json
    print("Received data:", data1) 
    user_id = data1.get('user_id')
    country = data1.get('country')
    input_data = {key: value for key, value in data1.items() if key not in ['user_id', 'country']}
    
    import pandas as pd
    input_data1 = pd.DataFrame(input_data, index=[0])
    
    
   
    prediction1 = model_national.predict(input_data1)
    
    GOOGLE_API_KEY = "AIzaSyC_Noz73FQAQxb4VrmW98RhFG81WbWX-2U"
    genai.configure(api_key=GOOGLE_API_KEY)
    genai_model = genai.GenerativeModel('gemini-1.5-flash')
    para_prompt = "provide me with some suggestions as to how carbon footprint can be reduced based on the data(its in percentage):(give me answer in only 5 points and nothing else, just 5 lines) the data is: cereal yeild, foreign district investment per gdp(in percentage), gross national income per capita, energy per capita, urbon population aggloration, protected area,population growth,uraban population groth percentage,"
    input_prompt_str = str(input_data1.to_dict(orient='records')[0])
    print(input_prompt_str)
    response = genai_model.generate_content(para_prompt + input_prompt_str)
    modified_text = re.sub(r'[\*\d]', '', response.text)
    points = modified_text.split('.')
    formatted_text = '\n'.join([point.strip() + '.' for point in points if point.strip()])
    
    print(formatted_text.encode('utf-8').decode('utf-8'))
    
    
    para_prompt2="give me the number of trees i owe to the enviornment based on the following info,just give me like a number, nothing else, no text nothing, just a number:"
    input_prompt_str2 = str(input_data1.to_dict(orient='records')[0])
    response2 = genai_model.generate_content(para_prompt2 + input_prompt_str2)
    
    print(response2.text)
    footprint = round(float(prediction1[0]) / 1000, 6)
    credit = footprint
    heat = round(footprint * 33.4, 6)
    tree = int(response2.text)

    # Insert the data into the "country" table
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        query = """
        INSERT INTO country (user_id, country, cereal, fdi, gni, energy, urban_pop_agg, protected_area, 
            pop_growth, urban_pop_growth, footprint, credits, heat, trees, suggestions)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            user_id, country, data1.get('cereal_yield'), data1.get('fdi_perc_gdp'),
            data1.get('gni_per_cap'), data1.get('en_per_cap'), data1.get('pop_urb_aggl_perc'),
            data1.get('prot_area_perc'), data1.get('pop_growth_perc'), data1.get('urb_pop_growth_perc'),
            footprint, credit, heat, tree, formatted_text
        )

        cursor.execute(query, values)
        connection.commit()  # Save changes to the database
        cursor.close()
        connection.close()

        print("National data inserted successfully.")
    else:
        print("Database connection failed.")
    
    return jsonify({'prediction': prediction1[0], 'suggestions': formatted_text, 'trees' : response2.text})


# Dummy user data for illustration
# users = {
#     'government_user': {'password': 'password123', 'role': 'government'},
#     'regular_user': {'password': 'password456', 'role': 'user'}
# }

@app.route('/process_login', methods=['POST'])
def process_login_action():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Query to retrieve user based on username
    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    user = cursor.fetchone()

    # Validate user credentials
    if user and user['password'] == password and user['role'] == role:
        session['user_id'] = user['user_id']  # Store user_id in session
        session['username'] = user['username']  # Optionally store username as well
        session['role'] = user['role']  # Store role if needed
        return jsonify({'success': True, 'role': user['role']})  # Successful login
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/register', methods=['POST'])
def register_user():
    # Get form data from the request
    user_id = request.form.get('user_id')
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm-password')
    role = request.form.get('role')

    # Check if passwords match
    if password != confirm_password:
        return "Passwords do not match.", 400

    # Connect to the database
    connection = get_db_connection()
    cursor = connection.cursor()

    # Insert the new user into the database
    query = """
        INSERT INTO users (user_id, username, password, role) 
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (user_id, username, password, role))
    connection.commit()

    # Close the connection
    cursor.close()
    connection.close()

    # Return a success message
    return "You are registered successfully!"



# Route to the company dashboard
@app.route('/government_dashboard')
def company_dashboard():
    return render_template("index.html")


@app.route('/individual_dashboard')
def individual_dashboard():
    # Check if the user is logged in (i.e., has a session)
    if 'user_id' not in session:
        return redirect('/login')  # Redirect to login page if not logged in

    user_id = session['user_id']
    username = session['username']

    # Connect to the database
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Query the database to get the user-specific data from the 'individual' table
    query = "SELECT * FROM individual WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    user_data = cursor.fetchone()  # Fetch the user's data

    cursor.close()
    connection.close()

    # If no data found, redirect to login page
    if not user_data:
        return redirect('/login')

    # Pass the user data to the template
    return render_template('user_view.html', user_data=user_data, username=username)

# @app.route('/country_dashboard')
# def user_dashboard():
#     return render_template("country.html")
# @app.route('/get_user_data', methods=['GET'])
# def get_user_data():
#     # Check if the user is logged in by checking session data
#     if 'user_id' not in session:
#         return jsonify({"error": "User not logged in"}), 401  # Return 401 if not logged in
    
#     user_id = session['user_id']  # Get user_id from session (make sure login sets this)
    
#     # Connect to the database
#     connection = get_db_connection()
#     if connection:
#         cursor = connection.cursor(dictionary=True)
        
#         # Query to get the user's carbon footprint data from the "individual" table
#         query = """
#         SELECT month, monthly_grocery_bill, vehicle_monthly_distance, waste_bag, tv_pc_hour, 
#                new_clothes, internet, material, cooking, body, sex, diet, shower, heating_source, 
#                social, travel_air, waste_bag_size, energy, transport, footprint, credits, heat, trees, suggestions
#         FROM individual
#         WHERE user_id = %s
#         ORDER BY month DESC LIMIT 12
#         """
        
#         cursor.execute(query, (user_id,))
#         rows = cursor.fetchall()
        
#         # Check if data is found
#         if rows:
#             # Prepare the data for the response
#             factors = [
#                 {"name": "Transportation", "value": row['vehicle_monthly_distance'] * 0.1} for row in rows
#             ]
#             monthly_data = [row['footprint'] for row in rows]  # Collect footprint values for the last 12 months

#             return jsonify({
#                 "success": True,
#                 "factors": factors,  # Carbon footprint factors (e.g., transportation, electricity, etc.)
#                 "monthlyData": monthly_data  # Monthly footprint data
#             })
#         else:
#             return jsonify({"error": "No data found for this user"}), 404
    
#     else:
#         return jsonify({"error": "Failed to connect to the database"}), 500


if __name__ == '__main__':
    app.run(debug=True)
