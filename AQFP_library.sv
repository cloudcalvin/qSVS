///////////////////////////////////////////
//////// Ramy Tadros & Arash Fayyazi 11/30/2018  ////////////
///////  AQFP modules in SV - Version-4
/////////////////////////////////////////////////

//`include "./AQFP_aux.sv"

/*the following is the list of macros that need to be defined in the topmodule
`localClkPW: the pulse width of the local clock. It has to be >0, so any small value would suffice
`clkDelay: the delay from clock in to clock out ... NOT NEEDED IN CASE OF SDF
`gateDelay: the propagation delay ... NOT NEEDED IN CASE OF SDF
`dataPW: data pulse width .. NOT NEEDED IN CASE OF SDF
`thold
`tsetup
*/


//-----------------------------------------------------------------------------------------------------
// -------------------------- LOGIC GATES  ------------------------------------------
//-----------------------------------------------------------------------------------------------------

///////////////////////////////////////////////////
module AQFPbuf1 (interface clkin, clkout, in, out);

	logicAQFP val; 
	
	AQFPclockPhase clk (clkin, clkout);
	AQFPsendModule snd (out);
	
	always begin
		clk.waitForSamplingPt();
		in.sample(val);
		snd.send(val);
	end
	
	AQFPtimingcheck1 TC0 (clk.localClk, in.data);
endmodule //buf1
///////////////////////////////////////////////////

///////////////////////////////////////////////////
module maj_ppp (interface clkin, clkout, a, b, c, out);

	logicAQFP vala, valb, valc, valout; 
	
	AQFPclockPhase clk (clkin, clkout);
	AQFPsendModule snd (out);
	
	always begin
		clk.waitForSamplingPt();
		a.sample(vala);
		b.sample(valb);
		c.sample(valc);
		valout = ((vala == qZ) || (valb == qZ) || (valc == qZ) || (vala == qX) || (valb == qX) || (valc == qX))? qZ:
					( ((vala == q1) && (valb == q1)) || ((vala == q1) && (valc == q1)) || ((valb == q1) && (valc == q1)) )? q1: q0; 
        snd.send(valout);
	end
	
	AQFPtimingcheck1 TCa (clk.localClk, a.data);
	AQFPtimingcheck1 TCb (clk.localClk, b.data);
	AQFPtimingcheck1 TCc (clk.localClk, c.data);

endmodule //maj_ppp

///////////////////////////////////////////////////

///////////////////////////////////////////////////
module maj_pnp (interface clkin, clkout, a, b, c, out);

	logicAQFP vala, valb, valc, valout; 
	
	AQFPclockPhase clk (clkin, clkout);
	AQFPsendModule snd (out);
	
	always begin
		clk.waitForSamplingPt();
		a.sample(vala);
		b.sample(valb);
		c.sample(valc);
		valout = ((vala == qZ) || (valb == qZ) || (valc == qZ) || (vala == qX) || (valb == qX) || (valc == qX))? qZ:
					( ((vala == q1) && (valb == q0)) || ((vala == q1) && (valc == q1)) || ((valb == q0) && (valc == q1)) )? q1: q0; 
        snd.send(valout);
	end
	
	AQFPtimingcheck1 TCa (clk.localClk, a.data);
	AQFPtimingcheck1 TCb (clk.localClk, b.data);
	AQFPtimingcheck1 TCc (clk.localClk, c.data);

endmodule //maj_pnp

///////////////////////////////////////////////////

///////////////////////////////////////////////////
module spl2 (interface clkin, clkout, in, out1, out2);

	logicAQFP val; 	
	
	AQFPclockPhase clk (clkin, clkout);
	AQFPsendModule snd1 (out1);
	AQFPsendModule snd2 (out2);
	
	always begin
		clk.waitForSamplingPt();
		in.sample(val);
		fork
		snd1.send(val);
		snd2.send(val);
		join
	end
	
	AQFPtimingcheck1 TC0 (clk.localClk, in.data);
endmodule //spl2

///////////////////////////////////////////////////

///////////////////////////////////////////////////
module spl3 (interface clkin, clkout, in, out1, out2, out3);

	logicAQFP val; 
	
		
	AQFPclockPhase clk (clkin, clkout);
	AQFPsendModule snd1 (out1);
	AQFPsendModule snd2 (out2);
	AQFPsendModule snd3 (out3);
	
	always begin
		clk.waitForSamplingPt();
		in.sample(val);
		fork
		snd1.send(val);
		snd2.send(val);
		snd3.send(val);
		join
	end
	
	AQFPtimingcheck TC0 (clk.localClk, in.data);
endmodule //spl3
///////////////////////////////////////////////////

///////////////////////////////////////////////////
module maj_npp (interface clkin, clkout, a, b, c, out);

	logicAQFP vala, valb, valc, valout; 
	
	AQFPclockPhase clk (clkin, clkout);
	AQFPsendModule snd (out);
	
	always begin
		clk.waitForSamplingPt();
		a.sample(vala);
		b.sample(valb);
		c.sample(valc);
		valout = ((vala == qZ) || (valb == qZ) || (valc == qZ) || (vala == qX) || (valb == qX) || (valc == qX))? qZ:
					( ((vala == q0) && (valb == q1)) || ((vala == q0) && (valc == q1)) || ((valb == q1) && (valc == q1)) )? q1: q0; 
        snd.send(valout);
	end
	
	AQFPtimingcheck1 TCa (clk.localClk, a.data);
	AQFPtimingcheck1 TCb (clk.localClk, b.data);
	AQFPtimingcheck1 TCc (clk.localClk, c.data);

endmodule //maj_npp

///////////////////////////////////////////////////


