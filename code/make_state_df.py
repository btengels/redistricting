from __future__ import division

import numpy as np

import pandas as pd
import geopandas as geo
import pickle
import shapely

import time


def make_state_census_dfs():
	'''
	Take the massive census dataframes of shape files and cut it up 
	into its individual states.
	'''	
	# congressional districts
	congress_geo  = geo.GeoDataFrame.from_file('../Data-Files/census/tl_2015_us_cd114/tl_2015_us_cd114.shp')	
	tract_geo_df  = geo.GeoDataFrame.from_file('../Data-Files/census/Tract_2010Census_DP1/Tract_2010Census_DP1.shp')		

	congress_geo.geometry = congress_geo.geometry.buffer(0)
	tract_geo_df.geometry = tract_geo_df.geometry.buffer(0)

	congress_geo['state'] = [i[0:2] for i in congress_geo.GEOID.values]
	tract_geo_df['state'] = [i[0:2] for i in tract_geo_df.GEOID10.values]

	for state in states:	
		print 'census', state

		state_id = states[state]				
		congress_geo_df = congress_geo[congress_geo.state==state_id]
		congress_geo_df.to_pickle('../Data-Files/'+state+'/congress_geo_'+state+'.p')

		tract_geo_df = tract_geo_df[tract_geo_df.state==state_id]
		tract_geo_df.to_pickle( '../Data-Files/'+state+'/tract_geo_'+state+'_df.p')



def get_current_districts(I_points,dist_geos):
	'''
	Function that gets current census district for each precinct
	'''
	# tic = time.time()
	n_precincts = len( I_points )
	n_districts = len( dist_geos )
	current_district = np.zeros((n_precincts,))
	for i in range( n_precincts ):

		# first see if the congressional district intersects the centroid of the precinct
		in_district = False
		i_d = 0
		while not in_district and i_d < n_districts:

			in_district = dist_geos[i_d].contains( I_points[i] ) 
			# print i, i_d, in_district
			i_d+=1
	
		if i_d <= n_districts:
			current_district[i] = int( i_d-1 )

		else: 
			# in some cases (islands), the centroids are not the most useful. 
			# so find the congressional district w/ the greatest intersection. 
			intersect_vector = np.zeros(n_districts)			
			for i_d in range(n_districts):

				intersect_vector[i_d] = dist_geos[i_d].intersection( I_points[i] ).area
		
			current_district[i] = int( np.argmax( intersect_vector ) )

	return current_district
	

def make_precinct_df(state, save_pickled_df=True):
	'''
	'''
	# ------------------------------------------------------------------------------------------
	# read in precinct data
	# ------------------------------------------------------------------------------------------
	precinct_geo = geo.GeoDataFrame.from_file('../Data-Files-simple/'+state+'/precinct/precinct.shp')
	lonlat =np.array([t.centroid.coords.xy for t in precinct_geo.geometry])
	precinct_geo['INTPTLON10'] = lonlat[:,0]
	precinct_geo['INTPTLAT10'] = lonlat[:,1]

	precinct_geo.geometry = precinct_geo.geometry.buffer(0)		
	try: 
		precinct_geo = precinct_geo.to_crs(crs=None, epsg=4326)
	except:
		pass
		
	state_id = states[state]

	if state in ['AL']:
		precinct_geo.rename(columns = {'USH_D_08' :'democrat','USH_R_08' :'republican'}, inplace = True)

	elif state in ['AZ']:
		precinct_geo.rename(columns = {'PRS08_DEM' :'democrat','PRS08_REP' :'republican'}, inplace = True)
	
	elif state in ['CA']:
		precinct_geo.rename(columns = {'CONDEM01' :'democrat','CONREP01' :'republican'}, inplace = True)

	elif state in ['CO']:		
		precinct_geo.rename(columns = {'USHSE10D'  :'democrat','USHSE10R'  :'republican'}, inplace = True)
	
	elif state in ['CT','MA']:
		precinct_geo.rename(columns = {'DEMOCRAT'  :'democrat','REPUBLICAN':'republican'}, inplace = True)
	
	elif state in ['FL']:
		precinct_geo.rename(columns = {'CONG_DEM_0':'democrat','CONG_REP_0':'republican'}, inplace = True)

	elif state in ['GA','MD','MN','OK','TN','WA']:
		precinct_geo.rename(columns = {'USH_DVOTE0':'democrat','USH_RVOTE0':'republican'}, inplace = True)

	elif state in ['HI', 'MS']:		
		precinct_geo.rename(columns = {'USP_D_08':'democrat','USP_R_08':'republican'}, inplace = True)
		precinct_geo.democrat.replace('NA',0, inplace=True)
		precinct_geo.republican.replace('NA',0, inplace=True)

	elif state in ['IA']:
		precinct_geo.rename(columns = {'USH_D_08':'democrat','USH_R_08':'republican'}, inplace = True)		
	
	elif state in ['ID']:
		precinct_geo.rename(columns = {'USH_D_06':'democrat','USH_R_06':'republican'}, inplace = True)				
	
	elif state in ['IL']:
		precinct_geo.rename(columns = {'OBAMA' :'democrat','MCCAIN':'republican'}, inplace = True)
		
	elif state in ['IN']:
		precinct_geo.rename(columns = {'OBAMA' :'democrat', 'MCCAIN':'republican'}, inplace = True)
		
	elif state in ['KS']:
		precinct_geo.rename(columns = {'PRES_D_08' :'democrat','PRES_R_08':'republican'}, inplace = True)	
	
	elif state in ['LA']:
		precinct_geo.rename(columns = {'USP_D_08_V' :'democrat','USP_R_08_V':'republican'}, inplace = True)

	elif state in ['MI']:
		precinct_geo.rename(columns = {'PRS08DEM' :'democrat','PRS08REP':'republican'}, inplace = True)

	elif state in ['MO']:
		precinct_geo.rename(columns = {'USH_DV08' :'democrat','USH_RV08' :'republican'}, inplace = True)
	
	elif state in ['NC']:
		precinct_geo.rename(columns = {'EL08G_PR_D' :'democrat','EL08G_PR_R' :'republican'}, inplace = True)		
	
	elif state in ['NE']:
		precinct_geo.rename(columns = {'USHDV08' :'democrat','USHRV08' :'republican'}, inplace = True)		

	elif state in ['NH']:
		precinct_geo.rename(columns = {'PRES_DVOTE' :'democrat','PRES_RVOTE' :'republican'}, inplace = True)		

	elif state in ['NJ']:
		precinct_geo.rename(columns = {'USP_DV_08' :'democrat','USP_RV_08' :'republican'}, inplace = True)		

	elif state in ['NM']:		
		precinct_geo.rename(columns = {'PRES_DEM_0' :'democrat','PRES_REP_0' :'republican'}, inplace = True)		

	elif state in ['NV']:		
		precinct_geo.rename(columns = {'USP_D_2008' :'democrat','USP_R_2008' :'republican'}, inplace = True)
	
	elif state in ['NY']:		
		precinct_geo.rename(columns = {'USS_6_DVOT' :'democrat','USS_6_RVOT' :'republican'}, inplace = True)						

	elif state in ['OH']:		
		precinct_geo.rename(columns = {'USH_DVOTE_' :'democrat','USH_RVOTE_' :'republican'}, inplace = True)						

	elif state in ['PA']:
		precinct_geo.rename(columns = {'USCDV2010' :'democrat','USCRV2010' :'republican'}, inplace = True)						
	
	elif state in ['SC']:
		precinct_geo.rename(columns = {'CONG08DEM' :'democrat','CONG08REP' :'republican'}, inplace = True)						

	elif state in ['TX']:
		precinct_geo.rename(columns = {'Pres_D_08' :'democrat','Pres_R_08' :'republican'}, inplace = True)						

	elif state in ['VA','UT','WV']:
		precinct_geo.rename(columns = {'PRES12_DEM' :'democrat','PRES12_REP' :'republican'}, inplace = True)
		precinct_geo.rename(columns = {'POP_BLACK' :'Black','POP_WHITE' :'White','POP_HISPAN':'Hispanic','POP_TOTAL':'total_pop'}, inplace = True)
		precinct_geo['Other'] = precinct_geo.total_pop - precinct_geo[['White','Black','Hispanic']].sum(axis=1)
		return precinct_geo[['democrat','republican','geometry','INTPTLON10','INTPTLAT10','White','Black','Hispanic','Other','total_pop']]

	elif state in ['WI']:
		precinct_geo.rename(columns = {'USH_04DEM' :'democrat','USH_04REP' :'republican'}, inplace = True)
		precinct_geo.rename(columns = {'WHITE' :'White','BLACK':'Black','OTHER' :'Other','HISPANIC':'Hispanic','PERSONS':'total_pop'}, inplace = True)
		precinct_geo.to_pickle('../Data-Files-simple/'+state+'/precinct_data_demographics.p')
		return precinct_geo[['democrat','republican','geometry','INTPTLON10','INTPTLAT10','White','Black','Hispanic','Other','total_pop']]

	precinct_geo.democrat = precinct_geo.democrat.astype(int)
	precinct_geo.republican = precinct_geo.republican.astype(int)

	precinct_data = precinct_geo[['democrat','republican','geometry','INTPTLON10','INTPTLAT10']]
	# ------------------------------------------------------------------------------------------
	# reading in congressional district data
	# ------------------------------------------------------------------------------------------	
	congress_geo = geo.GeoDataFrame.from_file( '../Data-Files-simple/'+state+'/congress_dist/congress.shp')	
	congress_geo = congress_geo.to_crs(crs=None, epsg=4326)

	n_districts = len( congress_geo )
	n_precincts = len( precinct_data )

	# ------------------------------------------------------------------------------------------
	# reading in census tract demographic data
	# ------------------------------------------------------------------------------------------
	tract_geo_df = geo.GeoDataFrame.from_file( '../Data-Files-simple/'+state+'/census_tract/census.shp')
	tract_geo_df = tract_geo_df.to_crs(crs=None, epsg=4326)

	# ------------------------------------------------------------------------------------------
	# get current districts
	# ------------------------------------------------------------------------------------------
	dist_geos = congress_geo.geometry.values
	I_points  = shapely.geometry.MultiPoint(precinct_data[['INTPTLON10','INTPTLAT10']].values.astype('float'))
	precinct_data['current_district'] = get_current_districts(I_points, dist_geos)	

	# ------------------------------------------------------------------------------------------
	# rename demographic variables of interest, toss out other census-tract variables
	# ------------------------------------------------------------------------------------------
	columns = {	'DP0040001': 'VA_total_pop' ,\
				'DP0110001': 'total_pop',\
				'DP0110002': 'Hispanic',\
				'DP0110011': 'White',\
				'DP0110012': 'Black',\
				'DP0110013': 'American_Indian',\
				'DP0110014': 'Asian',\
				'DP0110015': 'Hawaiian_Islander',\
				'DP0110016': 'Other',\
				'DP0110017': 'Two_or_more',\
				# 'DP0130001': 'Total_hh',\
				# 'DP0130002': 'hh_families',\
				# 'DP0130003': 'hh_families_families_w_children',\
				# 'DP0130004': 'hh_families_married',\
				# 'DP0130005': 'hh_families_married_w_children',\
				# 'DP0130006': 'hh_families_no_wife_present',\
				# 'DP0130007': 'hh_families_no_wife_present_w_children',\
				# 'DP0130008': 'hh_families_no_husband_present',\
				# 'DP0130009': 'hh_families_no_husband_present_w_children',\
				# 'DP0130010': 'hh_nonfamily'
				}

	tract_geo_df.rename(columns=columns, inplace=True)
	tract_geo_df['Other'] = tract_geo_df[['American_Indian','Asian','Hawaiian_Islander','Other']].sum(axis=0)	
	cols = [c for c in tract_geo_df.columns if c[0:2] != 'DP']
	tract_geo_df = tract_geo_df[cols]

	# ------------------------------------------------------------------------------------------
	# rename demographic variables of interest, toss out other census-tract variables
	# ------------------------------------------------------------------------------------------
	tract_array = tract_geo_df.geometry.values
	precinct_array = precinct_data.geometry.values


	tract_keys = [	'VA_total_pop' ,\
					'total_pop',\
					'Hispanic',\
					'White',\
					'Black',\
					'Other',\
					# 'Two_or_more',\
					# 'Total_hh',\
					# 'hh_families',\
					# 'hh_families_families_w_children',\
					# 'hh_families_married',\
					# 'hh_families_married_w_children',\
					# 'hh_families_no_wife_present',\
					# 'hh_families_no_wife_present_w_children',\
					# 'hh_families_no_husband_present',\
					# 'hh_families_no_husband_present_w_children',\
					# 'hh_nonfamily'
					]


	# ------------------------------------------------------------------------------------------
	# for each precinct, impute precinct-level demographics based on the weighted average of 
	# census-tracts. weights determined by fraction precinct intersecting with each census-tract
	# ------------------------------------------------------------------------------------------
	res_array = np.zeros( (n_precincts, len(tract_keys)) )
	mask = np.array([type(i)==shapely.geometry.polygon.Polygon for i in precinct_array])


	for i_p, precinct in enumerate(precinct_array):			 

		intersecting_tracts = np.where(np.array([precinct.intersects(t) for t in tract_array]) == True)[0]
		print i_p, i_p/n_precincts, intersecting_tracts
		frac_sum = 0
		for i_t in intersecting_tracts:			
			# find overlapping 
			frac_area = precinct.intersection(tract_array[i_t]).area/precinct.area
			
			for i_k, key in enumerate(tract_keys):
				
				tract_data = tract_geo_df[key].values[i_t]			
				res_array[i_p,i_k] += tract_data * frac_area


	for i_k, key in enumerate(tract_keys):
		precinct_data[key] = res_array[:,i_k]
	

	# ------------------------------------------------------------------------------------------
	# get current districts
	# ------------------------------------------------------------------------------------------		
	if save_pickled_df:
		precinct_data.to_pickle('../Data-Files-simple/'+state+'/precinct_data.p')
		
	return precinct_data



if __name__ == '__main__':
	
	tic = time.time()
	
	states = {					
				# 'AL':'01',
				# 'AZ':'04',
				# 'CA':'06', 
				# 'CO':'08', 
				# 'CT':'09', 
				# 'FL':'12', 
				# 'GA':'13', 
				# 'HI':'15', 
				# 'IA':'19', 
				# 'ID':'16', 
				# 'IL':'17', 
				# 'IN':'18', 
				# 'KS':'20', 
				# 'LA':'22', 
				# 'MA':'25', 
				# 'MD':'24', 
				# 'MI':'26', 
				# 'MN':'27', 
				# 'MO':'29', 
				# 'MS':'28',
				# 'NC':'37', 
				# 'NE':'31', 
				# 'NH':'33', 
				# # 'NJ':'34', 
				# 'NM':'35', 
				# 'NV':'32', 
				# 'NY':'36', 
				# # 'OH':'39', 
				# 'OK':'40', 
				# 'PA':'42', 
				# 'SC':'45', 
				# # 'TN':'47', 
				# 'TX':'48',
				# # 'UT':'49',#problem here
				'VA':'51',
				# 'WA':'53', 
				# 'WI':'55', 
				}
				

	for state in states: 
		print state, (time.time()-tic)/60.0		
		precinct_data = make_precinct_df(state)		


