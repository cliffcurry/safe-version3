print("time now=",calculations.tominutes(datetime.datetime.now()))       
            globs.actual_end_time=min(calculations.tominutes(globs.machineTable["end_time"]),
                                calculations.tominutes(globs.firstSwipePersonTable["end_time"]),
                                calculations.tominutes(globs.labTable["end_time"]))
            print("actual end time=",globs.actual_end_time)
            globs.actual_start_time=max(calculations.tominutes(globs.machineTable["start_time"]),
                                calculations.tominutes(globs.firstSwipePersonTable["start_time"]),
                                calculations.tominutes(globs.labTable["start_time"]))
            print("actual start time=",globs.actual_start_time)
            globs.user_name=globs.firstSwipePersonTable["name"]
            if (globs.user_name==None):
                Dis.display_message_to_user('ACCESS DENIED',3)
                Dis.display_message_to_user('because of',4)
                Dis.display_message_to_user('Unrecognized ID',5)
                state= st.WAIT_TO_RESET; first_time_here_flag=True  
                return (state,first_time_here_flag)  
            else:
                Dis.display_message_to_user(globs.user_name,1)
                if globs.firstSwipePersonTable["kind_of_person"]=="allAccess":
                    if globs.machineTable["uses_estop"]:
                        state=st.CALC_ACCESS_TIME; first_time_here_flag=True
                        return (state,first_time_here_flag)
                    else: 
                        state= st.SET_TIMER_FOR_SWITCH_DETECT ;first_time_here_flag=True
                        return (state,first_time_here_flag)
                (access,reason)=calculations.nonsupervisor_access(globs.actual_start_time,
                                            globs.actual_end_time,globs.first_swipe_prox_card,globs.machineTable["personAccessList"],
                                            globs.machineTable["kind_of_swipe_needed"])
                if access==False and reason=="Supervisor Swipe Needed": 
                    state= st.SUPERVISOR_NEEDED_CARD ;  first_time_here_flag=True
                    return (state,first_time_here_flag)      
                if access==True:
                    if globs.machineTable["uses_estop"]:
                        state=st.CALC_ACCESS_TIME; first_time_here_flag=True
                        return (state,first_time_here_flag)
                    else: 
                        state= st.SET_TIMER_FOR_SWITCH_DETECT ;first_time_here_flag=True
                        return (state,first_time_here_flag)
                if access==False and reason != "Supervisor Swipe Needed":      
                        Dis.display_message_to_user('ACCESS DENIED',3)
                        if (reason):
                            Dis.display_message_to_user(reason,4)
                        else:
                            Dis.display_message_to_user('Unknown reason ',4)
                        state= st.WAIT_TO_RESET;   first_time_here_flag=True 