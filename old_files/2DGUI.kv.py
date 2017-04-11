#File name: GUI2.py

<MotorButton@Button>:
    font_size: 20
    halign: 'left'
    valign: 'middle'


<QuitButton@Button>:
    text: 'Quit'
    font_size: 20
    pos_hint: {'right':1, 'bottom':0}
    size_hint: (0.2,0.1)
    
<DefaultLabel@Label>:
    font_size: 20
    halign: 'left'
    valign: 'middle'
    
<ControlPanelScreen>:
    BoxLayout:
        orientation: 'vertical'
        #Motor Settings Row
        BoxLayout:
            orientation: 'horizontal'
            DefaultLabel:
                text: "Motor"
            
            BoxLayout:
                orientation: 'vertical'
                MotorButton:
                    text: "Auto"
                    #on_release:
                MotorButton:
                    text: "Manual"
                    #on_release:
        	      MotorButton:
                    text: "Stop"		      
            BoxLayout:
                orientation: 'vertical'
                DefaultLabel: 
                    text: "PWM Val: " + str(manual_slider.value)
                Slider:
                    min: 0
                    max: 100
                    value: 50
                    step: 0.1
                    value_track: True
#                    value_track_color: 1, .3, .8, .5 3
                    id: manual_slider
        #Controller Settings Row   
        BoxLayout:
            orientation: 'horizontal'
            DefaultLabel:
                text: "Controller"
            #P box
            BoxLayout:
                orientation: 'vertical'
                BoxLayout:
                    orientation: 'horizontal'
                    DefaultLabel:
                        text: "P"
                    DefaultLabel:
                        text: str(p_slider.value)
                Slider:
                    min: 0
                    max: 10
                    value: 5
                    id: p_slider
            #I box
            BoxLayout:
                orientation: 'vertical'
                BoxLayout:
                    orientation: 'horizontal'
                    DefaultLabel:
                        text: "I"
                    DefaultLabel:
                        text: str(i_slider.value)
                Slider:
                    min: 0
                    max: 10
                    value: 5
                    id: i_slider
            #D box
            BoxLayout:
                orientation: 'vertical'
                BoxLayout:
                    orientation: 'horizontal'
                    DefaultLabel:
                        text: "D"
                    DefaultLabel:
                        text: str(d_slider.value)
                Slider:
                    min: 0
                    max: 10
                    value: 5
                    id: d_slider
        #Temperature Settings Row              
        BoxLayout:
            orientation: 'horizontal'
            DefaultLabel:
                text: "Temperature"
            GridLayout:
                cols: 3
                DefaultLabel:
                    text: "T(in)"
                DefaultLabel:
                    text: "T(out)"
                DefaultLabel:
                    text: "InitialTemp: " + str(initialtemp_slider.value)
                DefaultLabel:
                    text: "value of Tin"
                DefaultLabel:
                    text: "value of Tout" 
                Slider:
                    min: 0
                    max: 10
                    value: 5
                    id: initialtemp_slider