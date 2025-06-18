import numpy as np
import joblib
from tensorflow.keras.models import load_model

# Load the saved model and scaler
model = load_model("price_model.h5")
scaler = joblib.load("scaler.save")

# Define new input data (in the same feature order as during training!)
import numpy as np

new_data_raw = np.array([
    1,  # city (encoded)
    0,  # type (encoded)
    30.0,  # squareMeters
    1.0,   # rooms
    1.0,   # floor
    4.0,  # floorCount
    1970,  # buildYear (missing)
    54.503461,  # latitude
    18.543079,  # longitude
    1.0,       # centreDistance
    7.0,        # poiCount
    0.2,      # schoolDistance
    0.1,      # clinicDistance
    0.1,      # postOfficeDistance
    0.1,      # kindergartenDistance
    0.5,      # restaurantDistance
    0.9,      # collegeDistance
    0.05,      # pharmacyDistance
    0,  # ownership (encoded)
    0,  # buildingMaterial (encoded)
    0,  # condition (encoded or missing)
    0,  # hasParkingSpace
    1,  # hasBalcony
    1,  # hasElevator
    0,  # hasSecurity
    1,  # hasStorageRoom

    # distance_to_preschools
    0.3110682529650222,
    0.3943147915077087,
    0.4821331820385477,

    # distance_to_tram_and_bus_stops
    0.0574543080146068,
    0.1029241515606725,
    0.1809437628730109,

    # distance_to_primary_schools
    0.159507536069503,
    0.5400118855182604,
    0.5542913878305251,

    # distance_to_cultural_and_entertainment
    0.4571851517288916,
    0.4861854710532909,
    0.4943345657688207,

    # distance_to_train_stops
    0.6735774641511193,
    1.0324051185294283,
    1.3617607867113557,

    # distance_to_highschools_and_others
    0.185490872373957,
    0.4563818848603311,
    0.5089687449380959,

    # distance_to_green_spaces and scores
    10.787434207154469,    # distance_1
    596827085.0431135,     # score_1
    7.503262482668797,     # distance_2
    141666214.67789242,    # score_2
    9.898351116995416,     # distance_3
    88016523.65614952,     # score_3

    # distance_to_shopping_centers
    0.0887595599697756,
    0.1186704514146688,
    0.1489006083448613,

    # distance_to_utilities
    0.3406731240047017,
    0.6293409489039005,
    0.7336783754297379
])


# Scale the input
new_data_scaled = scaler.transform([new_data_raw])

# Predict
predicted_price = model.predict(new_data_scaled)
print(f"💰 Predicted price: ${predicted_price[0][0]:,.2f}")
