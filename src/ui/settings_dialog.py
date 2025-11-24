from PySide6 .QtWidgets import (QDialog ,QVBoxLayout ,QFormLayout ,QComboBox ,
QSpinBox ,QPushButton ,QColorDialog ,QSlider ,
QHBoxLayout ,QLabel ,QFontComboBox ,QCheckBox ,QGroupBox ,QScrollArea ,QWidget )
from PySide6 .QtCore import Qt 
from PySide6 .QtGui import QFont 
from src .utils .translations import TRANSLATIONS 
from src .core .system_monitor import SystemMonitor 

class SettingsDialog (QDialog ):
    def __init__ (self ,config_manager ,on_apply_callback =None ,parent =None ):
        super ().__init__ (parent )
        self .config_manager =config_manager 
        self .on_apply_callback =on_apply_callback 
        self .current_lang =self .config_manager .get ("language","es")
        self .initialized =False 
        self .apply_stylesheet ()
        self .init_ui ()
        self .retranslate_ui ()
        self .initialized =True 


        self .on_preset_change (self .preset_combo .currentIndex ())

    def apply_stylesheet (self ):
        self .setStyleSheet ("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
            }
            QComboBox, QSpinBox, QFontComboBox {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 4px;
            }
            QComboBox::drop-down, QFontComboBox::drop-down {
                border: 0px;
            }
            QComboBox QAbstractItemView, QFontComboBox QAbstractItemView {
                background-color: #3c3c3c;
                color: #ffffff;
                selection-background-color: #4CAF50;
            }
            QCheckBox {
                color: #ffffff;
                font-size: 14px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #555555;
                border-radius: 4px;
                background-color: #3c3c3c;
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
                border: 1px solid #4CAF50;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3e8e41;
            }
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #3c3c3c;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4CAF50;
                border: 1px solid #4CAF50;
                width: 18px;
                height: 18px;
                margin: -7px 0;
                border-radius: 9px;
            }
            QGroupBox {
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 3px;
                color: #4CAF50;
                font-weight: bold;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #2b2b2b;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #555555;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #4CAF50;
            }
            QScrollBar::add-line:vertical {
                height: 0px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }
            QScrollBar::sub-line:vertical {
                height: 0px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

    def init_ui (self ):
        main_layout =QVBoxLayout ()

        scroll_area =QScrollArea ()
        scroll_area .setWidgetResizable (True )
        scroll_area .setHorizontalScrollBarPolicy (Qt .ScrollBarAlwaysOff )
        scroll_content =QWidget ()
        scroll_layout =QVBoxLayout (scroll_content )


        self .group_general =QGroupBox ()
        general_layout =QFormLayout ()


        self .lang_label =QLabel ()
        self .lang_combo =QComboBox ()
        self .lang_combo .addItems (["en","es"])
        self .lang_combo .setCurrentText (self .current_lang )
        self .lang_combo .currentTextChanged .connect (self .on_language_change )
        general_layout .addRow (self .lang_label ,self .lang_combo )

        self .group_general .setLayout (general_layout )
        scroll_layout .addWidget (self .group_general )


        self .group_appearance =QGroupBox ()
        appearance_layout =QFormLayout ()


        self .font_family_label =QLabel ()
        self .font_family_combo =QFontComboBox ()
        self .font_family_combo .setCurrentFont (QFont (self .config_manager .get ("font_family","Arial")))
        appearance_layout .addRow (self .font_family_label ,self .font_family_combo )


        self .font_size_label =QLabel ()
        self .font_size_spin =QSpinBox ()
        self .font_size_spin .setRange (8 ,72 )
        self .font_size_spin .setValue (self .config_manager .get ("font_size",14 ))
        appearance_layout .addRow (self .font_size_label ,self .font_size_spin )


        self .text_color_label =QLabel ()
        self .text_color_btn =QPushButton ()
        self .text_color =self .config_manager .get ("text_color","#FFFFFF")
        self .text_color_btn .setStyleSheet (f"background-color: {self .text_color }")
        self .text_color_btn .clicked .connect (lambda :self .pick_color ("text"))
        appearance_layout .addRow (self .text_color_label ,self .text_color_btn )


        self .bg_color_label =QLabel ()
        self .bg_color_btn =QPushButton ()
        self .bg_color =self .config_manager .get ("background_color","#000000")
        self .bg_color_btn .setStyleSheet (f"background-color: {self .bg_color }")
        self .bg_color_btn .clicked .connect (lambda :self .pick_color ("bg"))
        appearance_layout .addRow (self .bg_color_label ,self .bg_color_btn )


        self .opacity_label =QLabel ()
        self .opacity_slider =QSlider (Qt .Horizontal )
        self .opacity_slider .setRange (0 ,100 )
        self .opacity_slider .setValue (int (self .config_manager .get ("background_opacity",0.5 )*100 ))
        appearance_layout .addRow (self .opacity_label ,self .opacity_slider )

        self .group_appearance .setLayout (appearance_layout )
        scroll_layout .addWidget (self .group_appearance )


        self .group_position =QGroupBox ()
        position_layout =QFormLayout ()


        self .preset_label =QLabel ()
        self .preset_combo =QComboBox ()
        self .preset_combo .addItem ("custom","custom")
        self .preset_combo .addItem ("top-left","top-left")
        self .preset_combo .addItem ("top-center","top-center")
        self .preset_combo .addItem ("top-right","top-right")
        self .preset_combo .addItem ("bottom-left","bottom-left")
        self .preset_combo .addItem ("bottom-center","bottom-center")
        self .preset_combo .addItem ("bottom-right","bottom-right")

        current_preset =self .config_manager .get ("position_preset","custom")
        index =self .preset_combo .findData (current_preset )
        if index >=0 :
            self .preset_combo .setCurrentIndex (index )

        self .preset_combo .currentIndexChanged .connect (self .on_preset_change )
        position_layout .addRow (self .preset_label ,self .preset_combo )


        self .custom_pos_layout =QHBoxLayout ()

        self .pos_label =QLabel ()
        self .pos_x_label =QLabel ()
        self .pos_x_spin =QSpinBox ()
        self .pos_x_spin .setRange (0 ,3000 )
        self .pos_x_spin .setValue (self .config_manager .get ("position_x",10 ))

        self .pos_y_label =QLabel ()
        self .pos_y_spin =QSpinBox ()
        self .pos_y_spin .setRange (0 ,2000 )
        self .pos_y_spin .setValue (self .config_manager .get ("position_y",10 ))

        self .custom_pos_layout .addWidget (self .pos_label )
        self .custom_pos_layout .addWidget (self .pos_x_label )
        self .custom_pos_layout .addWidget (self .pos_x_spin )
        self .custom_pos_layout .addWidget (self .pos_y_label )
        self .custom_pos_layout .addWidget (self .pos_y_spin )
        self .custom_pos_layout .addStretch ()

        position_layout .addRow (self .custom_pos_layout )

        self .group_position .setLayout (position_layout )
        scroll_layout .addWidget (self .group_position )


        self .group_content =QGroupBox ()
        content_layout =QFormLayout ()


        self .show_time_check =QCheckBox ()
        self .show_time_check .setChecked (self .config_manager .get ("show_time",True ))
        content_layout .addRow ("",self .show_time_check )

        self .show_cpu_check =QCheckBox ()
        self .show_cpu_check .setChecked (self .config_manager .get ("show_cpu",True ))
        content_layout .addRow ("",self .show_cpu_check )

        self .show_cpu_name_check =QCheckBox ()
        self .show_cpu_name_check .setChecked (self .config_manager .get ("show_cpu_name",False ))
        content_layout .addRow ("",self .show_cpu_name_check )

        self .show_ram_check =QCheckBox ()
        self .show_ram_check .setChecked (self .config_manager .get ("show_ram",True ))
        content_layout .addRow ("",self .show_ram_check )


        self .show_gpu_name_check =QCheckBox ()
        self .show_gpu_name_check .setChecked (self .config_manager .get ("show_gpu_name",True ))
        content_layout .addRow ("",self .show_gpu_name_check )


        self .monitor =SystemMonitor ()
        gpu_info =self .monitor .get_gpu_info ()
        self .gpu_checks ={}

        gpu_visibility =self .config_manager .get ("gpu_visibility",{})

        if gpu_info :
            gpu_label =QLabel ("GPUs:")
            content_layout .addRow (gpu_label )
            for name ,_ in gpu_info :
                check =QCheckBox (name )

                is_visible =gpu_visibility .get (name ,True )
                check .setChecked (is_visible )
                content_layout .addRow ("",check )
                self .gpu_checks [name ]=check 
                check .toggled .connect (lambda :self .save_settings ())

        self .group_content .setLayout (content_layout )
        scroll_layout .addWidget (self .group_content )

        scroll_area .setWidget (scroll_content )
        main_layout .addWidget (scroll_area )
        self .setLayout (main_layout )


        self .font_family_combo .currentFontChanged .connect (lambda :self .save_settings ())
        self .font_size_spin .valueChanged .connect (lambda :self .save_settings ())
        self .pos_x_spin .valueChanged .connect (lambda :self .save_settings ())
        self .pos_y_spin .valueChanged .connect (lambda :self .save_settings ())
        self .opacity_slider .valueChanged .connect (lambda :self .save_settings ())
        self .show_time_check .toggled .connect (lambda :self .save_settings ())
        self .show_cpu_check .toggled .connect (lambda :self .save_settings ())
        self .show_cpu_name_check .toggled .connect (lambda :self .save_settings ())
        self .show_ram_check .toggled .connect (lambda :self .save_settings ())
        self .show_gpu_name_check .toggled .connect (lambda :self .save_settings ())

    def retranslate_ui (self ):
        trans =TRANSLATIONS .get (self .current_lang ,TRANSLATIONS ["en"])
        self .setWindowTitle (trans ["settings"])

        self .group_general .setTitle (trans ["tab_general"])
        self .group_appearance .setTitle (trans ["tab_appearance"])
        self .group_position .setTitle (trans ["tab_position"])
        self .group_content .setTitle (trans ["tab_content"])

        self .lang_label .setText (trans ["language"])
        self .preset_label .setText (trans ["position_preset"])
        self .preset_combo .setItemText (0 ,trans ["preset_custom"])
        self .preset_combo .setItemText (1 ,trans ["preset_top_left"])
        self .preset_combo .setItemText (2 ,trans ["preset_top_center"])
        self .preset_combo .setItemText (3 ,trans ["preset_top_right"])
        self .preset_combo .setItemText (4 ,trans ["preset_bottom_left"])
        self .preset_combo .setItemText (5 ,trans ["preset_bottom_center"])
        self .preset_combo .setItemText (6 ,trans ["preset_bottom_right"])
        self .pos_label .setText (trans ["position_label"])
        self .pos_x_label .setText (trans ["axis_x"])
        self .pos_y_label .setText (trans ["axis_y"])
        self .font_family_label .setText (trans ["font_family"])
        self .font_size_label .setText (trans ["font_size"])
        self .text_color_label .setText (trans ["text_color"])
        self .text_color_btn .setText (trans ["pick_color"])
        self .bg_color_label .setText (trans ["bg_color"])
        self .bg_color_btn .setText (trans ["pick_color"])
        self .opacity_label .setText (trans ["opacity"])
        self .show_time_check .setText (trans ["show_time"])
        self .show_cpu_check .setText (trans ["show_cpu"])
        self .show_cpu_name_check .setText (trans ["show_cpu_name"])
        self .show_ram_check .setText (trans ["show_ram"])
        self .show_gpu_name_check .setText (trans ["show_gpu_name"])

    def on_preset_change (self ,index ):
        key =self .preset_combo .itemData (index )
        is_custom =(key =="custom")
        self .pos_x_spin .setEnabled (is_custom )
        self .pos_y_spin .setEnabled (is_custom )
        self .save_settings ()

    def pick_color (self ,target ):
        color =QColorDialog .getColor ()
        if color .isValid ():
            hex_color =color .name ()
            if target =="text":
                self .text_color =hex_color 
                self .text_color_btn .setStyleSheet (f"background-color: {hex_color }")
            else :
                self .bg_color =hex_color 
                self .bg_color_btn .setStyleSheet (f"background-color: {hex_color }")
            self .save_settings ()

    def on_language_change (self ,text ):
        self .current_lang =text 
        self .retranslate_ui ()
        self .save_settings ()

    def save_settings (self ):
        if not hasattr (self ,'initialized')or not self .initialized :
            return 

        self .config_manager .set ("language",self .lang_combo .currentText ())
        self .config_manager .set ("position_preset",self .preset_combo .currentData ())
        self .config_manager .set ("font_family",self .font_family_combo .currentFont ().family ())
        self .config_manager .set ("font_size",self .font_size_spin .value ())
        self .config_manager .set ("position_x",self .pos_x_spin .value ())
        self .config_manager .set ("position_y",self .pos_y_spin .value ())
        self .config_manager .set ("text_color",self .text_color )
        self .config_manager .set ("background_color",self .bg_color )
        self .config_manager .set ("background_opacity",self .opacity_slider .value ()/100.0 )
        self .config_manager .set ("show_time",self .show_time_check .isChecked ())
        self .config_manager .set ("show_cpu",self .show_cpu_check .isChecked ())
        self .config_manager .set ("show_cpu_name",self .show_cpu_name_check .isChecked ())
        self .config_manager .set ("show_ram",self .show_ram_check .isChecked ())
        self .config_manager .set ("show_gpu_name",self .show_gpu_name_check .isChecked ())

        gpu_visibility ={}
        for name ,check in self .gpu_checks .items ():
            gpu_visibility [name ]=check .isChecked ()
        self .config_manager .set ("gpu_visibility",gpu_visibility )

        self .config_manager .save_config ()

        if self .on_apply_callback :
            self .on_apply_callback ()
