package net.zc7.util;

import org.javatuples.Triplet;

public class Geobox {
	private final double[] LON_BOUND = {-180, 180};
	private final double[] LAT_BOUND = {-90, 90};
	private final double[] SIZE = {LON_BOUND[1]-LON_BOUND[0], LAT_BOUND[1]-LAT_BOUND[0]};
	
	private int depth;
	private double[] gpoint;
	private long gcode;
	
	
	/**
	 * Initialize Geobox with geo location, default depth to 32
	 * @param lon
	 * @param lat
	 */
	public Geobox(double lon, double lat) {
		// Default depth to 32
		this(lon, lat, 32);
	}
	
	public Geobox(double lon, double lat, int depth) {
		this.depth = depth;
		gpoint = new double[]{lon, lat};
		gcode = calcGeocode(lon, lat, depth);
	}
	

	/**
	 * For given position, compare it to the mid point between lower bound (lbound) and
	 * upper bound (ubound).  If after mid point, return 1 and set new lower bound as
	 * mid point.  Otherwise return 0 and set upper bound as mid point.
	 * 
	 * @param position
	 * @param lbound
	 * @param ubound
	 * @return bit, lres, ures as array
	 */
	private Triplet<Boolean, Double, Double> findPosition(double position, double lbound, double ubound) {
		boolean bit;
		double lres;
		double ures;
		// System.out.println("lbound: " + lbound + "; ubound: " + ubound);
		double mid = (lbound + ubound) / 2.0;
		// System.out.println("pos: " + position + "; mid: " + mid);
		if (position > mid) {
			bit = true;
			lres = mid;
			ures = ubound;
		} else {
			bit = false;
			lres = lbound;
			ures = mid;
		}
		// System.out.println("lres" + lres + "; ures: " + ures);
		
		return new Triplet<Boolean, Double, Double>(bit, lres, ures);
	}
	
	private long calcGeocode(double lon, double lat, int depth) {
		double lon_lbound = this.LON_BOUND[0];
		double lon_ubound = this.LON_BOUND[1];
		double lat_lbound = this.LAT_BOUND[0];
		double lat_ubound = this.LAT_BOUND[1];
		
		long result = 0;
		
		for(int l=0; l<depth; l++) {
			Triplet<Boolean, Double, Double> lon_pos = findPosition(lon, lon_lbound, lon_ubound);
			boolean lon_bit = lon_pos.getValue0();
			lon_lbound = lon_pos.getValue1();
			lon_ubound = lon_pos.getValue2();
			
			Triplet<Boolean, Double, Double> lat_pos = findPosition(lat, lat_lbound, lat_ubound);
			boolean lat_bit = lat_pos.getValue0();
			lat_lbound = lat_pos.getValue1();
			lat_ubound = lat_pos.getValue2();
			
			// reverse the index
			int i = depth - l;
			
			// Calculate the interleave value
			int result_index = i * 2 - 1;
			
			if (lon_bit) {
				result += 1L << result_index;
			}
			
			if (lat_bit) {
				result += 1L << (result_index-1);
			}
						
			// System.out.println("Pos:" + result_index + ", lon:" + lon_bit + "; lat:" + lat_bit + ": result=" + result + "; bin:" + Long.toBinaryString(result));
			
		}

		return result;
	}

	// Generated getter/setter
	public int getDepth() {
		return depth;
	}

	public double[] getGpoint() {
		return gpoint;
	}

	public long getGcode() {
		return gcode;
	}
	
	

}
