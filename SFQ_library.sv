///////////////////////////////////////////
//////// Ramy Tadros 08/15/2018  ////////////
///////  HCLC allowed modules in SV - Version-5
/////////////////////////////////////////////////

/*the following is the list of macros that need to be defined in the topmodule for testing (no SDF)
`pw: any small value would suffice (1e-3)
`tsetup
`thold
`tgate
*/

`include "./SFQ_aux.sv"

module SFQand2 (SFQ clkin, in1, in2, out);
	
	SFQpropagationDelay gPD ();
	
	always begin
		clkin.receive();
		if (in1.isReceived(1'b1) & in2.isReceived(1'b1)) begin
			gPD.tPD();
			out.send();
		end
	end
	
	SFQtimingcheck2 TC (clkin.data, in1.data, in2.data);
endmodule //and2
///////////////////////////////////////////////////

///////////////////////////////////////////////////
module SFQbuf1 (SFQ clkin, in, out);
	
	SFQpropagationDelay gPD ();
	
	always begin
		clkin.receive();
		if (in.isReceived(1'b1)) begin
			gPD.tPD();
			out.send();
		end
	end
	
	SFQtimingcheck1 TC (clkin.data, in.data);
endmodule //buf1
///////////////////////////////////////////////////

///////////////////////////////////////////////////
module SFQsplit (SFQ in, out1, out2);
	
	SFQpropagationDelay gPD1 ();
	SFQpropagationDelay gPD2 ();

	always begin
		in.receive();
		fork
			begin
				gPD1.tPD();
				out1.send();	
			end
			begin
				gPD2.tPD();
				out2.send();
			end
		join
	end
endmodule // split 
///////////////////////////////////////////////////




