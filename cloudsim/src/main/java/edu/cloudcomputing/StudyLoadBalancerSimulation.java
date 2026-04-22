# Study Load Balancer - CloudSim Simulation
# Maps study scheduling concepts to cloud computing entities

import cloudsim.*;
import org.cloudhub.util.*;
import java.util.*;

/**
 * StudyLoadBalancerSimulation simulates a student study schedule
 * using CloudSim's infrastructure-as-a-service model.
 * 
 * Mapping:
 * - Study Hours -> Cloud resource (CPU time in Million Instructions)
 * - Subject -> Virtual Machine (VM)
 * - Difficulty -> MIPS rating (processing capacity)
 * - Individual Study Session -> Cloudlet (task)
 * - Deadline -> Cloudlet deadline constraint
 */
public class StudyLoadBalancerSimulation {
    
    private List<Cloudlet> cloudletList;
    private List<Vm> vmList;
    private DatacenterBroker broker;
    
    public static void main(String[] args) {
        StudyLoadBalancerSimulation simulation = new StudyLoadBalancerSimulation();
        simulation.run();
    }
    
    public void run() {
        Log.println("=== Cloud-Based Study Load Balancer Simulation ===");
        
        // Step 1: Initialize CloudSim
        int numUser = 1;
        Calendar calendar = Calendar.getInstance();
        boolean traceFlag = false;
        CloudSim.init(numUser, calendar, traceFlag);
        
        // Step 2: Create Datacenter
        Datacenter datacenter0 = createDatacenter("Datacenter_0");
        
        // Step 3: Create Broker
        broker = new DatacenterBroker("StudyBroker");
        
        // Step 4: Create Subject VMs (mapped from study subjects)
        vmList = createSubjectVMs(5);
        broker.submitVmList(vmList);
        
        // Step 5: Create Study Cloudlets (mapped from study sessions)
        cloudletList = createStudyCloudlets();
        broker.submitCloudletList(cloudletList);
        
        // Step 6: Start simulation
        CloudSim.startSimulation();
        
        // Step 7: Collect results
        List<Cloudlet> resultList = broker.getCloudletReceivedList();
        
        // Step 8: Print metrics
        printSimulationMetrics(resultList);
        
        CloudSim.stopSimulation();
        Log.println("Simulation completed successfully!");
    }
    
    private Datacenter createDatacenter(String name) {
        List<Host> hostList = new ArrayList<>();
        
        // Host with 8 CPU cores, 8192 MB RAM
        int hostId = 0;
        int ram = 8192;
        long storage = 1000000;
        int bw = 10000;
        int pesNumber = 8;
        
        // MIPS = 1000 per core (simulates study capacity)
        double mips = 1000;
        Host host = new Host(hostId, ram, bw, storage, pesNumber, new SimpleVmPe(mips, new PeProvisionerSimple()), new FileProvisionerSimple());
        hostList.add(host);
        
        // Create datacenter characteristics
        String architecture = "x86";
        String os = "Linux";
        String vmm = "Xen";
        double time_zone = 9.0;
        double cost = 3.0;
        double costPerMem = 0.05;
        double costPerStorage = 0.01;
        double costPerBw = 0.05;
        
        DatacenterCharacteristics characteristics = 
            new DatacenterCharacteristics(architecture, os, vmm, hostList, time_zone, cost, costPerMem, costPerStorage, costPerBw);
        
        // Create datacenter
        Datacenter datacenter = null;
        try {
            datacenter = new Datacenter(name, characteristics, new VmAllocationPolicySimple(hostList), new LinkedList<>(), 0);
        } catch (Exception e) {
            e.printStackTrace();
        }
        
        return datacenter;
    }
    
    private List<Vm> createSubjectVMs(int numSubjects) {
        List<Vm> vms = new ArrayList<>();
        
        String[] subjects = {"Mathematics", "Physics", "Chemistry", "Biology", "English"};
        int[] difficulties = {5, 4, 3, 4, 2};  // Difficulty 1-5 maps to MIPS
        
        for (int i = 0; i < numSubjects; i++) {
            int vmid = i;
            int mips = difficulties[i] * 250;  // Higher difficulty = more MIPS
            long size = 10000;
            int ram = 512;
            long bw = 1000;
            
            Vm vm = new Vm(vmid, broker.getId(), mips, difficulties[i], ram, bw, size, "Xen", new CloudletSchedulerTimeShared());
            vms.add(vm);
        }
        
        return vms;
    }
    
    private List<Cloudlet> createStudyCloudlets() {
        List<Cloudlet> cloudlets = new ArrayList<>();
        
        // Study session parameters
        long[] sessionLengths = {4000, 3200, 2400, 3200, 1600};  // Tied to difficulty
        int pesNumber = 1;
        long fileSize = 300;
        long outputSize = 300;
        UtilizationModelFull um = new UtilizationModelFull();
        
        for (int i = 0; i < sessionLengths.length; i++) {
            Cloudlet cloudlet = new Cloudlet(i, sessionLengths[i], pesNumber, fileSize, outputSize, um, um, um);
            cloudlet.setUserId(broker.getId());
            cloudletList.add(cloudlet);
        }
        
        // Set deadlines (in simulation time units)
        cloudletList.get(2).setDeadline(100);  // Chemistry due earlier
        
        return cloudlets;
    }
    
    private void printSimulationMetrics(List<Cloudlet> cloudlets) {
        Log.println("\n=== Simulation Results ===");
        
        double totalCompletionTime = 0;
        double totalPlannedTime = 0;
        int completed = 0;
        
        for (Cloudlet cl : cloudlets) {
            totalCompletionTime += cl.getFinishTime();
            totalPlannedTime += cl.getCloudletLength();
            
            if (cl.getCloudletStatus() == Cloudlet.SUCCESS) {
                completed++;
            }
        }
        
        // Metric 1: Completion Time
        double avgCompletionTime = totalCompletionTime / cloudlets.size();
        Log.printlnf("Avg Completion Time: %.2f time units", avgCompletionTime);
        
        // Metric 2: Jain's Fairness Index
        double[] completionRates = new double[cloudlets.size()];
        for (int i = 0; i < cloudlets.size(); i++) {
            completionRates[i] = cloudlets.get(i).getFinishTime() > 0 ? 1.0 : 0.0;
        }
        double fairnessIndex = calculateJainsFairnessIndex(completionRates);
        Log.printlnf("Fairness Index (Jain): %.3f", fairnessIndex);
        
        // Metric 3: Resource Utilization
        double utilizationPercent = (avgCompletionTime / 150.0) * 100;
        Log.printlnf("Resource Utilization: %.1f%%", utilizationPercent);
        
        // Metric 4: Success Rate
        double successRate = (completed * 100.0) / cloudlets.size();
        Log.printlnf("Task Success Rate: %.1f%%", successRate);
    }
    
    /**
     * Jain's Fairness Index calculation
     * Formula: (sum(xi))^2 / (n * sum(xi^2))
     * Range: 0 to 1, where 1 is perfectly fair
     */
    private double calculateJainsFairnessIndex(double[] values) {
        if (values.length == 0) return 1.0;
        
        double sum = 0;
        double sumSquares = 0;
        
        for (double v : values) {
            sum += v;
            sumSquares += v * v;
        }
        
        if (sumSquares == 0) return 1.0;
        
        return (sum * sum) / (values.length * sumSquares);
    }
}