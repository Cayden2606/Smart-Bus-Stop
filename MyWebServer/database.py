import sqlite3

conn = sqlite3.connect('busStop.db')
c = conn.cursor()

# Create environment table
# c.execute("""
# CREATE TABLE environment (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
#     temperature DECIMAL,
#     humidity DECIMAL,
#     noise INT,
#     voc DECIMAL,
#     light DECIMAL,
#     pressure DECIMAL
# )
# """)

# # Create activity table
# c.execute("""
# CREATE TABLE activity (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
#     edge_warning BOOLEAN,
#     bus_detected DECIMAL,
#     human_presence BOOLEAN,
#     emergency BOOLEAN,
#     minor_emergency
#     rating INTEGER
# )
# """)

# c.execute("""
# CREATE TABLE ping (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
#     BBBW1 BOOLEAN,
#     BBBW2 BOOLEAN,
#     BBBW3 BOOLEAN,
#     BBBW4 BOOLEAN   
# )
# """)

# c.execute("""
# CREATE TABLE bus (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     bus_number TEXT,
#     actual_arrive_time DATETIME DEFAULT CURRENT_TIMESTAMP,
#     predicted_arrive_time DATETIME,
#     difference_in_time TEXT
# )
# """)

c.execute("""
CREATE TABLE settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    edge_force_threshold DECIMAL,
    edge_ir_dist_threshold DECIMAL,
    edge_prox_threshold DECIMAL,
    bus_force_threshold DECIMAL,
    lighting_prox_threshold DECIMAL,
    led_target DECIMAL
)
""")
# Uncomment and create interaction table if needed
# c.execute("""
# CREATE TABLE interaction (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
#     button_pressed BOOLEAN,
#     feedback TEXT,
#     emergency_call BOOLEAN,
#     estimated_arrival_time TIME,
#     actual_arrival_time TIME
# )
# """)

# Commit and close connection
conn.commit()
conn.close()
