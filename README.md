# py-hive
A demo of the python libraries for the Hive MapReduce architecture.

- [Hadoop Install](hadoop-install)
- [Run Job With Python](python)

# Hadoop Install

### Java 7 Installation
- Enter these commands in terminal
```
sudo add-apt-repository ppa:webupd8team/java
sudo apt-get update
sudo apt-get install oracle-jdk7-installer
```

### Create Hadoop User
- Create the user
```
sudo addgroup hadoop
sudo adduser --ingroup hadoop hduser
password: hadoop
```

- Switch to the hduser
```
su hduser
password: hadoop
```

- Create ssh key and add it as an authorized key
```
ssh-keygen  -t rsa -P ""
cp ~/.ssh/id_rsa.pub ~/.ssh/authorized_keys
```

- Install ssh and connect to localhost
```
sudo apt-get install ssh
ssh localhost
```

- Exit from the hduser and download the hadoop files into a folder. Extract the files and put them into the usr local files.
```
exit
wget http://apache.mirror.gtcomm.net/hadoop/common/hadoop-2.7.3/hadoop-2.7.3.tar.gz
sudo tar xvzf hadoop-2.7.3.tar.gz
sudo mv hadoop-2.7.3 /usr/local/hadoop
```

- Change the owner of the hadoop files in `usr/local/hadoop` to the hduser
```
cd /usr/local/
sudo chown -R hduser:hadoop hadoop
```

- Edit the bash rc file as hduser
```
su hduser
nano ~/.bashrc
```

- Add this to the file. Remember that ctrl+shft+v is how to paste in terminal.
```bash
  # Environment variable for Hadoop location, include bin in the path
  export HADOOP_HOME=/usr/local/hadoop
  export PATH=$PATH:$HADOOP_HOME/bin

  # Environment varibale for Java location
  export JAVA_HOME=/usr/lib/jvm/java-7-oracle

  # Hadoop related aliases
  unalias fs &> /dev/null
  alias fs="hadoop fs"
  unalias hls &> /dev/null
  alias hls="fs -ls"
```

- You need to reload bash from the change rc file.
```
source ~/.bashrc
```

- Switch back to the main user, make a hadoop app directory and switch back to the hduser.
```
exit
sudo mkdir -p /app/hadoop/tmp
sudo chown -R hduser:hadoop /app/hadoop/tmp
su hduser
```

- Edit the core site xml file
```
nano /usr/local/hadoop/etc/hadoop/core-site.xml
```

- In the configuration tags, insert this

```xml
<property>
  <name>hadoop.tmp.dir</name>
  <value>/app/hadoop/tmp</value>
        <description>A base for other temporary directories.</description>
  </property>


  <property>
  <name>fs.default.name</name>
  <value>hdfs://localhost:54310</value>
  <description>The name of the default file system.  A URI whose
  scheme and authority determine the FileSystem implementation.
  The uri's scheme determines the config property (fs.SCHEME.impl)
  naming the FileSystem implementation class. The uri's authority
  is used to determine the host, port, etc. for a filesystem.</description>
</property>
```

- Edit the mapred-site xml file
```
nano /usr/local/hadoop/etc/hadoop/mapred-site.xml.template
```

- In the configuration tags, add this

```xml
<property>
<name>mapred.job.tracker</name>
<value>localhost:54311</value>
<description>The host and port that the MapReduce job tracker runs
at. If "local", then jobs are run in-process as a single map and reduce task.
</description>
</property>
```

- Edit the hdfs xml file
```
nano /usr/local/hadoop/etc/hadoop/hdfs-site.xml
```

- Put this in the configuration tags

```xml
<property>
<name>dfs.replication</name>
<value>1</value>
<description>Default block replication. The actual number of replications
can be specified when the file is created. The default is used if replication
is not specified in create time.</description>
</property>
```

- Edit the hadoop environment file to add the location of the java JDK
```
nano /usr/local/hadoop/etc/hadoop/hadoop-env.sh
```

- Add this at the end of the file.
```
export JAVA_HOME=/usr/lib/jvm/java-7-oracle
```

- Format the hadoop file system
```
hdfs namenode -format
```

### Start Hadoop Cluster

- Run this command to start the cluster and get the local address.
- Make sure you execute this as hduser
```
su hduser
/usr/local/hadoop/sbin/start-dfs.sh
```

- you can get summaries of the nodes running with the `jps` command

- You should get this at `localhost:50070`

![HadoopStartup](img/HadoopStartup.png)

- In order to stop, run this command

```
/usr/local/hadoop/sbin/stop-dfs.sh
```

# Python


### Map and Reduce Scripts

- First, lets setup the libraries

```
cd /py-hive
pip install -r requirements.txt
```

- Run the population scripts to get csvs of data.

```
python populate.py
```

- Switch back to the hadoop user and add some hdfs data from the csvs into the hadoop storage

```
su hduser
hdfs dfs mkdir /user
hdfs dfs mkdir /user/data
hdfs dfs -put /home/neil/projects/py-hive/data/* /user/data
```

- Display the copied data

```
hdfs dfs -ls /user/data

Found 5 items
-rw-r--r--   1 hduser supergroup      25209 2016-11-02 17:15 /user/data/hustle.csv
-rw-r--r--   1 hduser supergroup      35777 2016-11-02 17:15 /user/data/overall_defense.csv
-rw-r--r--   1 hduser supergroup      34513 2016-11-02 17:15 /user/data/rim.csv
-rw-r--r--   1 hduser supergroup      44592 2016-11-02 17:15 /user/data/speed.csv
-rw-r--r--   1 hduser supergroup      65409 2016-11-02 17:15 /user/data/zone_shooting.csv
```

- Add map script

```
nano /home/hduser/count_mapper.py
```

- Copy into map scripts


```python
#!/usr/bin/env python

import sys

for line in sys.stdin:
    line = line.decode('utf-8')
    line = line.split(',')
    team_abr = line[3]
    # map key value pair of team abbreviation and intermediate count
    print "%s\t%i" % (team_abr, 1)
```

- Add reduce script

```
nano /home/hduser/count_reducer.py
```


- Copy this to reduce script


```python
#!/usr/bin/env python

import sys

current_abr = None
current_count = 0
abr = None

for line in sys.stdin:
    abr, count = line.split('\t')
    count = int(count)
    if abr == current_abr:
        current_count += count
    else:
        if current_abr:
            print '%s\t%i' % (current_abr, current_count)
        current_abr = abr
        current_count = count

if current_abr == abr:
    # map current reduced key value pai
    print '%s\t%i' % (current_abr, current_count)
```

- Run the map and reduce jobs. Make sure to run in `~`

```
cd ~/
hadoop jar /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-2.7.3.jar -file /home/hduser/count_mapper.py -mapper /home/hduser/count_mapper.py -file /home/hduser/count_reducer.py -reducer /home/hduser/count_reducer.py -input /user/data/rim.csv -output /user/data/rim-output
```

- It should run without error. To see the output, enter this to view the output document in hadoop.

```
hdfs dfs -cat /user/data/rim-output/part-00000
```

- To run the jobs again, you need to remove the output file.

```
hdfs dfs -rm -r /user/data/rim-output
```

### Browsing the HDFS

- If you still have hadoop running, you can view the files in output from the web browser as well.

- Go to `http://localhost:50070/explorer.html` and add the directory that you want to explore.

![Directory](img/directory.png)
