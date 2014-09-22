# -*- coding: utf-8 -*-
from collections import OrderedDict


DATE_TIME, MILLIS, T_EXT, T_INT, T_ENT, T_SOR, T_CON, PCHAUF, HC, MOI, TMOI, TEMP = range(12)

TABLE_NAME = ('millis', 't_ext', 't_int', 't_ent', 
              't_sor', 't_con', 'pchauf', 'hc', 'moi', 'tmoi')

ID_TO_NAME = OrderedDict([(MILLIS, u'compteur de millisecondes'),
             (T_EXT, u'température extérieure'),
             (T_INT, u'température intérieure'),
             (T_ENT, u'entrée de chaudière'),
             (T_SOR, u'sortie de chaudière'),
             (T_CON, u'consigne de température'),
             (PCHAUF, u'puissance'),
             (HC, u'heures creuses/pleines'),
             (MOI, u'capteur d\'humidité'),
             (TMOI, u'température du capteur'),
             ]
                         
            )


COLORS = ('#0000FF', '#5F9EA0', '#8A2BE2', '#A52A2A', '#7FFF00', '#D2691E', '#00FFFF',
          '#B8860B','#8B008B', '#FF8C00', '#E9967A', '#FF1493')

DAY, WEEK, MONTH, YEAR = range(4)