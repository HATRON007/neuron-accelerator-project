`timescale 1ns / 1ps 

module tb_fhn;
    // Signal Declarations
    reg clk, rst;
    reg signed [15 : 0] i_stim;
    wire signed [15 : 0] v_out, w_out;

    // Fixed-Point Parameters (Q3.12)
    localparam FRC_BITS = 12;
    real scaling_factor = 4096.0;

    // Instantiate the Core
    core uut(
        .clk(clk), 
        .rst(rst), 
        .i(i_stim),
        .v(v_out), 
        .w_out(w_out)
    );

    // Clock Generation (100 MHz -> 10ns period)
    initial clk = 0;
    always #5 clk = ~clk;
    
    integer file;

    initial begin 
        // Optional: Create VCD for GTKWave
        $dumpfile("fhn_sim.vcd");
        $dumpvars(0, tb_fhn);

        // Open CSV file for Python plotting
        file = $fopen("data.csv", "w");
        if (file == 0) begin
            $display("Error: Could not open file.");
            $finish;
        end
        
        // Header for CSV
        $fdisplay(file, "time_step,v_raw,v_float");

        // 1. Initialization
        rst = 1; 
        i_stim = 0;
        #100;
        
        // 2. Release Reset
        rst = 0;
        #100; 

        // 3. Apply Stimulus
        // Value 3277 corresponds to ~0.8 in Q3.12 format
        // Paper uses I=0.5 (2048) or I=1.0 (4096) for testing.
        i_stim = 16'd4096; 
        $display("Applying Stimulus I = 0.8...");

        // Run for 4000 cycles (Spiking Phase)
        repeat (4000) begin
            @(posedge clk); // Wait for clock edge
            // Write simulation time, raw integer, and converted float approximation
            $fdisplay(file, "%0d,%d,%f", $time, $signed(v_out), $signed(v_out)/scaling_factor);
        end

        // 4. Remove Stimulus (Relaxation Phase)
        i_stim = 16'd0;
        $display("Removing Stimulus...");

        repeat (20000) begin
            @(posedge clk);
            $fdisplay(file, "%0d,%d,%f", $time, $signed(v_out), $signed(v_out)/scaling_factor);
        end

        $display("Simulation Finished. Data written to data.csv");
        $fclose(file);
        $finish;
    end

endmodule