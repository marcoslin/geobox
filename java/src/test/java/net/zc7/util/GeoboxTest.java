package net.zc7.util;

import org.junit.Test;
import static org.junit.Assert.assertEquals;

public class GeoboxTest {
	@Test
	public void testInt() {
		Long i = 1L << 63;
		i += (1L << 62);
		
		long expected = Long.parseLong("100000000000000000000000000000000000000000000000000000000000000", 2);
		expected *= -1;
		
		System.out.println("Expected: " + expected);
		System.out.println("Expected (bitCount): " + Long.bitCount(expected));
		System.out.println("Expected (toBinaryString): " + Long.toBinaryString(expected));
		
		System.out.println("Int: " + i);
		System.out.println("Int (bitCount): " + Long.bitCount(i));
		System.out.println("Int (toBinaryString): " + Long.toBinaryString(i));
	}
	
	
	@Test
	public void testSimpleContractCreation() {
		Geobox g = new Geobox(12.481563961993402, 41.87643118161227);
		
		assertEquals(-4195692029019287352L, g.getGcode());
	}

}
