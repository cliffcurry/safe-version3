first_swipe_reason='not on user list'
user_touched_screen_flag=False
SOFTWARE_VERSION=" 0.99"
my_mac_address='00:89:90:ab:34'  # retrieved in the display routine,,,very first thing
first_swipe_prox_card="12345"
second_swipe_prox_card="123456"
in_extended_time_state=False   # a global state variable to make the second swipe logic re-usable
interlockTable={'mac':'00:89:90:ab:34', 'manufacturing_date':'2018-04-05',
                        'controller_serial_number':1,'relay_box_serial_number': 3}

machineTable=  {'machine_id':2,'university_inventory_number':'078976-977','manufacturer_serial_number':'97866-a97','name': 'Grinder',
            'lab_containing_machine': 'b-103', 'kind_of_swipe_needed': 'Single', 
            'start_time': '12:00', 'end_time': '18:30', 
           
            'minutes_enabled': 5, 'uses_estop': False}
firstSwipePersonTable={'university_id':'clicurry','name': 'Clifford Curry', 'kind_of_person': 'faculty', 'start_date':'2018-09-05',
                        'end_date':'2018-09-05','start_time': '5:00', 'end_time': '14:30'}
                        
secondSwipePersonTable={'university_id':'jkostman','name': 'John Kostman', 'kind_of_person': 'student', 'start_date':'2018-10-08',
                        'end_date':'2018-12-14','start_time': '8:00', 'end_time': '14:30'}
                        
labTable={'name': 'DFM lab', 'room':'106 SC','start_time': '5:00', 'end_time': '14:30'}

actual_end_time=456
actual_start_time=299
user_access_minutes=30