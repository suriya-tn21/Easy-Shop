import streamlit as st
from PIL import Image
import io
import User
import Product
import datetime

image1 = Image.open("Images/image1.png")

def Home_page():
    col1, col2 = st.columns(2)
    with col1:
        st.header("Give Your Workout A New Style!")
        st.write("Success isn't always about greatness. It's about consistency. Consistent hard work gains success. Greatness will come.")
    with col2:
        st.image(image1)
    
    st.subheader("Sponsored Products")
    sponsored_products = Product.fetch_sponsored_products()
    if sponsored_products:
        display_product_list(sponsored_products, "home")
    else:
        st.write("No sponsored products available at the moment.")

    st.subheader("All Products")
    other_products = Product.fetch_other_products()
    display_product_list(other_products, "home")
    
def display_product_list(products, page):
    if page == "home":
        products = products[:4]
    cols = st.columns(4)
    for i, product in enumerate(products):
        with cols[i % 4]:
            if product[1] and isinstance(product[1], bytes):
                try:
                    image = Image.open(io.BytesIO(product[1]))
                    st.image(image, use_column_width=True)
                except Exception as e:
                    st.write(f"Error loading image: {e}")
                    st.write("No image available")
            else:
                st.write("No image available")
            
            st.markdown(f"##### {product[6]}")
            st.write(f"Seller: {product[9]}")
            st.write(f"Rs. {product[7]}")
            if st.button("Details", key=f"details_{product[0]}"):
                st.session_state.selected_product = product
                st.session_state.page = 'Product Details'
                st.rerun()

def All_products_page():
    st.title("All Products")
    st.session_state.search_query = st.text_input("Search for products", value=st.session_state.search_query)
    sort_option = st.selectbox("Sort by", ("Default Sorting", "Sort by price", "Sort by popularity", "Sort by rating", "Sort by sale"))
    
    st.write("---")
    products = Product.fetch_products()

    if products:
        if User.check_owner_acc():
            for product in products:
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.subheader(product[6])  # Product name
                    st.write(f"Price: Rs. {product[7]}")
                    st.write(f"Seller: {product[9]}")
                    st.write(f"Description: {product[8]}")
                
                with col2:
                    if product[1]:  # Assuming the first image is at index 1
                        image = Image.open(io.BytesIO(product[1]))
                        st.image(image, width=100)
                    else:
                        st.write("No image available")
                
                with col3:
                    if product[11]:  # Sponsored status
                        if st.button("Remove Sponsorship", key=f"unsponsored_{product[0]}"):
                            Product.remove_sponsorship(product[0])
                            st.success("Product removed from sponsored list")
                            st.rerun()
                    else:
                        if st.button("Make Sponsored", key=f"sponsor_{product[0]}"):
                            Product.make_sponsored(product[0])
                            st.success("Product added to sponsored list")
                            st.rerun()
                    
                    if st.button("Delete Product", key=f"delete_{product[0]}"):
                        Product.delete_product(product[0])
                        st.success("Product deleted successfully")
                        st.rerun()
                
                st.write("---")
        else:
            display_product_list(products, "Products")
    else:
        st.write("No products available at the moment.")
        
def Product_details_page():
    st.title("Product Details")
    if 'selected_product' in st.session_state:
        product = st.session_state.selected_product
        
        if st.button("← Back"):
            st.session_state['page'] = 'Products'
            st.rerun()
    
        image_container = st.container()
        with image_container:
            cols = st.columns(5)
            for i, img_data in enumerate(product[1:5]):  # First 5 elements are image data
                if img_data:
                    image = Image.open(io.BytesIO(img_data))
                    resized_image = Product.resize_image(image)
                    with cols[i]:
                        st.image(resized_image, use_column_width=True)
                else:
                    with cols[i]:
                        st.write("")
        
        # Display product details
        st.subheader(product[5])  # Product name
        st.write(f"Price: Rs. {product[6]}")  # Product price
        st.write(f"Description: {product[7]}")  # Product description

        seller_username = product[8]  # Assuming the 9th item is the seller's username
        seller_email = product[9]  # Assuming the 10th item is the seller's email

        seller_details = User.fetch_user_details(seller_username)
        st.subheader("About the Seller")
        if seller_details:
            if seller_details['profile_pic']:
                profile_image = Image.open(io.BytesIO(seller_details['profile_pic']))
                resized_image = profile_image.resize((100, 100))
                st.image(resized_image, use_column_width=False)
            else:
                st.write("No profile picture available.")
            
            st.write(f"**Name:** {seller_username}")
            st.write(f"**Email:** {seller_email}")
            st.write(f"**Phone:** {seller_details['phone']}")
            
            if seller_details['bio']:
                st.write("**Biography:** "  + seller_details['bio'])
            else:
                st.write("Not provided.")
        else:
            st.write("Seller information not available.")

    else:
        st.write("No product selected.")

def About_page():
    st.title("About Us")
    st.write("Easy Shop is your one-stop destination for a wide range of products.")

def Account_page():
    # Check if the user is logged in and show the profile page if true
    if User.get_signed_in_acc():
        show_profile_page(User.get_signed_in_acc())
    else:
        # Otherwise, show the login and registration tabs
        st.title("Sign in | Sign up")
        login_tab, register_tab, reset_tab = st.tabs(["Login", "Register", "Reset Password"])

        with login_tab:
            st.subheader("Login")
            login_username = st.text_input("Username", key="login_username")
            login_password = st.text_input("Password", type="password", key="login_password")

            if st.button("Login"):
                if User.sign_in(login_username, login_password):
                    st.success("Logged in successfully")
                    st.rerun()  # This refreshes the page to switch to the profile view
                else:
                    st.error("Login failed. Check your credentials.")

        with register_tab:
            st.subheader("Sign Up")
            reg_username = st.text_input("Username", key="reg_username")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            reg_confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_password")
            reg_email = st.text_input("Email", key="reg_email")
            reg_phone = st.text_input("Phone Number", key="reg_phone")
            reg_dob = st.date_input("Date of Birth", key="reg_dob", min_value = datetime.date(1970, 1, 1), max_value=datetime.date(2200, 12, 31))
            reg_profile_pic = st.file_uploader("Profile Picture", type=["png", "jpg", "jpeg"], key="reg_profile_pic")
            reg_bio = st.text_area("Biography", key="reg_bio")

            if st.button("Sign up"):
                if len(reg_password) >= 8:
                    if reg_password == reg_confirm_password:
                        result = User.sign_up(reg_username, reg_password, reg_email, reg_phone, reg_dob, reg_profile_pic, reg_bio)
                        if "Account Created Successfully" in result:
                            st.success("Account Created Successfully")
                            recovery_key = result.split("Your recovery key is: ")[1]
                            st.warning(f"Please save your recovery key: {recovery_key}")
                            st.info("You can use this key to reset your password if you forget it.")
                        else:
                            st.error("Username Already Exists")
                    else:
                        st.error("Passwords do not match.")
                else:
                    st.error("Passwords Should be More than 8 Characters")
                 
        with reset_tab:
            st.subheader("Reset Password")
            reset_username = st.text_input("Username", key="reset_username")
            reset_recovery_key = st.text_input("Recovery Key", key="reset_recovery_key")
            reset_new_password = st.text_input("New Password", type="password", key="reset_new_password")
            reset_confirm_password = st.text_input("Confirm New Password", type="password", key="reset_confirm_password")

            if st.button("Reset Password"):
                if reset_new_password == reset_confirm_password:
                    if len(reset_new_password) >= 8:
                        result = User.reset_pas(reset_username, reset_recovery_key, reset_new_password)
                        if "Password reset successful" in result:
                            st.success(result)
                        else:
                            st.error(result)
                    else:
                        st.error("Password must be at least 8 characters long.")
                else:
                    st.error("New passwords do not match.")
        
def show_profile_page(username):
    if username == User.owner_user:
        st.title(f"Welcome, {username}!")
        st.divider()
        
        col1, col2 = st.columns([1, 3])

        with col1:
            profile_image = Image.open("Images\\Owner Profile.jpg")
            #resized_image = profile_image.resize((256, 256))
            st.image(profile_image, use_column_width=True)
        
        with col2:
            st.subheader("Profile Information")
            st.write(f"**Username:** {User.owner_user}")
            st.write(f"**Email:** {User.owner_account}")
            

    else:    
        st.title(f"Welcome, {username}!")
        st.divider()
        user_details = User.fetch_user_details(username)

        if user_details:
            col1, col2 = st.columns([1, 3])

            with col1:
                if user_details['profile_pic']:
                    profile_image = Image.open(io.BytesIO(user_details['profile_pic']))
                    resized_image = profile_image.resize((256, 256))
                    st.image(resized_image, use_column_width=True)
                else:
                    st.write("No profile picture available.")
            
            with col2:
                st.subheader("Profile Information")
                st.write(f"**Username:** {user_details['username']}")
                st.write(f"**Email:** {user_details['email']}")
                st.write(f"**Phone Number:** {user_details['phone']}")
                st.write(f"**Date of Birth:** {user_details['dob']}")
                
                st.subheader("Biography")
                st.write(user_details['bio'])

            st.divider()
            st.subheader("Account Actions")
            if st.button("Edit Profile"):
                st.session_state['page'] = 'Edit Profile'
                st.rerun()
            if st.button("Change Password"):
                st.session_state["page"] = "Change Password"
                st.rerun()
            if st.button("Log Out"):
                User.sign_out()
                st.rerun()  

        else:
            st.error("Failed to fetch profile details.")
      
def Add_Product_page():
    if not User.get_signed_in_acc():
        st.error("You must be logged in to add a product.")
        st.write("Please go to the Account page to sign in or create an account.")
        return
    
    st.title("Add Product")
    st.write("Please fill in the details below to add your product:")
    
    # Allow up to 5 images to be uploaded
    product_images = [st.file_uploader(f"Choose image {i+1} (optional)", type=["png", "jpg", "jpeg"]) for i in range(5)]
    
    product_name = st.text_input("Product Name")
    product_price = st.text_input("Price")
    product_description = st.text_area("Description")
    
    if st.button("Submit"):
        if product_name and product_price and product_description:
            # Convert uploaded files to PIL images
            images = [Image.open(image) if image else None for image in product_images]
            
            Product.add_product(images, product_name, product_price, product_description, User.get_signed_in_acc(), User.get_email(User.get_signed_in_acc()))
            st.success("Product added successfully!")
        else:
            st.error("Please fill in all required fields.")

def Edit_Profile_page():
    username = st.session_state.get('username')    
    user_details = User.fetch_user_details(username)
    
    if user_details:
        st.title(f"Edit Profile: {username}")
        st.markdown("---")
        
        new_email = st.text_input("Email", value=user_details['email'])
        new_phone = st.text_input("Phone Number", value=user_details['phone'])

        # Convert the date string to a datetime.date object
        try:
            current_dob = datetime.datetime.strptime(user_details['dob'], '%Y-%m-%d').date()
        except (ValueError, TypeError):
            current_dob = datetime.date.today()  # Use today's date as a fallback

        new_dob = st.date_input("Date of Birth", value=current_dob)
        new_profile_pic = st.file_uploader("Update Profile Picture (optional)", type=["png", "jpg", "jpeg"])
        new_bio = st.text_area("Biography", value=user_details['bio'])
        
        if st.button("Save Changes"):
            User.update_profile(username, new_email, new_phone, new_dob, new_profile_pic, new_bio)
            st.success("Profile updated successfully!")
            st.session_state['page'] = 'Account'  # Return to the Account page after saving
            st.rerun()
        
        if st.button("Cancel"):
            st.session_state['page'] = 'Account'  # Return to the Account page without saving
            st.rerun()
            
    else:
        st.error("Failed to fetch user details.")

def Change_password_page():
    st.subheader("Change Password")
    current_password = st.text_input("Current Password", type="password")
    new_password = st.text_input("New Password", type="password")
    confirm_new_password = st.text_input("Confirm New Password", type="password")
    if st.button("Change Password"):
        if new_password == confirm_new_password:
            result = User.change_pas(User.get_signed_in_acc(), current_password, new_password)
            if result[0] == "Password Changed":
                st.success(result[1])
            else:
                st.error(result[1])
        else:
            st.error("New passwords do not match.")
    
    if st.button("Cancel"):
        st.session_state['page'] = 'Account'
        st.rerun()

def All_account_page():
    st.title("All User Accounts")
    
    if not User.check_owner_acc():
        st.error("You don't have permission to view this page.")
        return
    
    users = User.fetch_all_users()
    
    if not users:
        st.warning("No user accounts found.")
        return
    
    for user in users:
        username, email, phone, dob, bio = user
        
        st.subheader(f"User: {username}")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**Email:** {email}")
            st.write(f"**Phone:** {phone}")
            st.write(f"**Date of Birth:** {dob}")
        
        with col2:
            st.write("**Biography:**")
            st.write(bio if bio else "No biography provided.")
        
        st.divider()

        with col3:
            if st.button("Delete Account", key=f"delete_{username}"):
                if User.delete_user_by_username(username):
                    st.success(f"Account {username} has been deleted.")
                    st.rerun()
                else:
                    st.error(f"Failed to delete account {username}.")
