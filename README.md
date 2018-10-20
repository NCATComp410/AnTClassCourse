Class Project- North Carolina A&T State University

This demonstrates the sample usecases of router and traffic generator deployed in AWS cloud.

Getting Started:

Clone this repository on your local machine and get started. Please refer below link if any help needed on cloning a repository.
https://help.github.com/articles/cloning-a-repository/

Prerequisites:

- Python version 3

- Use below command to get all the required packages to run sample tests.

  pip install -r requirements.txt
 
- More info about packages used.
  PyYAML pacakges
  https://pyyaml.org/wiki/PyYAMLDocumentation
  Paramiko - A Python implementation of SSHv2
  http://www.paramiko.org/installing.html

Running the script:

You have to be inside the cloned repository and can simply run like any other python script.

Author:

Sachin Daware

Support:

Please reach out to me at sdaware@cisco.com for any queries.

Device Contention Problem:

Part of the goal for this assignment was to allow the class to experience real-world agile development challenges and find ways to work between scrum teams to solve them.  

One such problem is the one Sachin and I presented last week in class - managing  testbed contention.  While we provided a working example which included the (5) test case code, (6) device-under-test, and (4) traffic generation (https://github.com/sdaware/AnTClassCourse) it was noted that there were no checks in place to keep multiple users from stepping on each other while a test case was executing.  

It is up to the (1/2) execution engine to solve this problem and manage testbed resources.  Before a test case is executed, the execution engine will determine which devices are necessary (traffic generation and DUT), reserve them, execute the test case, and then release the reservation so that the next test case can execute. 

However, the execution engine doesn’t exist yet.  This is a classic chicken-before-the-egg type problem we face routinely during agile development.

In order for other teams to make progress, such as developing new test cases, there needs to be a temporary mechanism in place to manage resource contention.  While there are potentially many possible ways to solve this problem, your thoughts should go towards the quickest and simplest approach.

Looking over the sample test case (https://github.com/sdaware/AnTClassCourse) - I see that the connection to the traffic generator is the first connection made to the testbed:

	status = connect_traffic_gen(params,retries=5)

Looking more into this function I see that once the connection is established, traffic generation begins:

	…

	traffic_gen.connect( params["traffic_gen"]["IP"], port=22, username = params["traffic_gen"]["Username"], password = params["traffic_gen"]
	["Password"],allow_agent=False,look_for_keys=False,auth_timeout=30,passphrase=None)

	…

	print('\nConnected to traffic generator...preparing to run traffc...')
	stdin,stdout,stderr = traffic_gen.exec_command('cd trex/v2.24;./runtrex')

It is also worth noting at this point that the (4) traffic generation tool is Cisco TRex (https://trex-tgn.cisco.com/)

This makes me think about two possible solutions to the contention issue.  (1) check first to see if another user is connected to the traffic generator or (2) check to see if there is an existing TRex instance running.  

To test out the first idea I first need to determine how to manually connect to the traffic generator.  Looking at the topology.pdf provided I can find the login information. This could be done either with ssh or with putty depending on your development environment. 

ssh ec2-user@13.58.108.166

    [ec2-user@ip-10-1-1-33 ~]$ users
    ec2-user ec2-user

The ‘users’ command shows me that there are currently two instances of the ec2-user connected to the system.  Determining if the testbed is in use simply by looking to see if another user is connected is probably too heavy-handed because someone may need to connect at times to do system administration or other activities not directly related to running a test case. 

The second idea was to check to see if there is an existing instance of TRex running.  The ‘ps’ command is useful for this.  Referring back to the sampleUseCase.py script I see the command used to generate the traffic:

	print('\nConnected to traffic generator...preparing to run traffc...')
	stdin,stdout,stderr = traffic_gen.exec_command('cd trex/v2.24;./runtrex')

So, I could use the ps command to check to see if there is already a ‘runtrex’ instance:

    [ec2-user@ip-10-1-1-33 ~]$ ps -ef | grep runtrex
    ec2-user   3145   2554  0 17:17 pts/2    00:00:00 grep --color=auto runtrex

Here I see my grep process and nothing else.  Now I’ll start the sampleUseCase.py and then execute the same command:

	AnTClassCourse/sampleUseCase.py
	Connecting to traffic generator 13.58.108.166

	Connected to traffic generator...preparing to run traffc...

    [ec2-user@ip-10-1-1-33 ~]$ ps -ef | grep runtrex
    ec2-user   3149   3148  0 17:19 ?        00:00:00 bash -c cd trex/v2.24;./runtrex
    ec2-user   3158   3149  0 17:19 ?        00:00:00 bash -c cd trex/v2.24;./runtrex
    ec2-user   3213   2554  0 17:19 pts/2    00:00:00 grep --color=auto runtrex

Here I can see there are now ‘runtrex’ processes running.  I can use this information to add some code to my script to avoid stepping on someone else:

def is_testbed_available(traffic_gen):
    # Get process info including runtrex string
    stdin,stdout,stderr = traffic_gen.exec_command('ps -ef | grep runtrex')

    # search through the output of the ps command
    for line in stdout.readlines():
        # if a line contains runtrex
        if re.search(r'runtrex', line):
            # and it doesn't contain grep
            if not re.search(r'grep', line):
                # the testbed is busy - so return False
                print('The testbed is busy!')
                return False

    # Did not find any instances of runtrex
    return True

Now I can use this new function in the sample code and won’t accidentally step on someone else’s test in process. 
