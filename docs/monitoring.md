
This swift deployment includes the option to enable monitoring allowing investigation of performance issues and questions.
In this version we include the option to gather system data during the deployment and in general, providing performance insights on proxy and storage nodes. This includes metrics such as memory consumption by XFS inodes, object database size, and memory and CPU utilization of the services accessing those databases.
All of this is done also with the option for full customisation and the abiility to add aditional metrics that should be collected and  custom dashboards.


 The monitoring functionality is based on PCP - Performance Co-Pilot, which provides real-time and historical performance data collection, analysis, and visualization capabilities. With PCP, its possible to gather detailed metrics on system resources, such as CPU, memory, disk I/O, and network usage, along with application-specific data.
 PCP also inlucdes Redis integration allowing persistant storage allowing to replay past data to troubleshoot issues that occurred at specific points in time. In addition it includes integration with Grfana introducing customizable dashboards that present the data collected by pcp.

# Setup

the monitoring script uses pcp nasible so it must be installed by running:

```
ansible-galaxy collection install performancecopilot.metrics
```

also its required to install jsonnet ad described in https://github.com/google/jsonnet

and in case of adding new jsonnrt liibraries also jb is required that can be installed by folloen gthe instructions here: https://github.com/jsonnet-bundler/jsonnet-bundler


also need to install python grafana-client package by running:

```
 pip install grafana-client
```



# Builtin features

Swiftaucular provides as part of its setup a full working out of the box monitoring tool. the monitoring addition includes a grafana instance hosted on a dedicated vm created at setup. and configures the storage and proxy nodes to include perssistant storage of the metrics collected by using the integrated pcp-redis option. the grafana intance is configured with the pcp-redis datasources for all of the nodes. the precreated dashboards are alspo created automativcaly in the grafana instance. in this section we will exaplin ib detail all the existing features.

## complete monitoring+swift deployment script

Swiftaucular includes  `run_with_monitor` script - that setups the monitoring, and runs the deployment and workload tests while recording the monitored metrics.
Thre script creates all the neccasy vms for the swift deployment and the monitoring. Then starts with starting the monitoring setup by calling the ansible playbook
`monitor_swift_cluster.yaml` that setups the grafana instance and pcp configuration.the `monitor_swift_cluster.yaml` plyabook uses pcp-ansible to installl pcp and grafana https://github.com/performancecopilot/ansible-pcp. after that it creates the dashboards by calling a python script that can be found in monitoring/grafana/configure_grafana.py. After the creation of the dashbpards URLs to the dashobards will be printed out containg live version of the reocrded metrics. When accseesing the grafana instnace a username and password is required, the default is user: admin password: admin. On the first acces you will be requested to change it.
Imidatley after the creation of the dashboards the deployment phase will start, and at the end of it URLs to the dashboards containg the exact time frame of the deployment with be outputed. allowing an option to investigate the results in a later time. the same will happen for the workload tests.


example output:
```
```


## swiftdbinfo PMDA

In addition to collecting metrics on system resources pcp allows collection of application-specific data by allowing csutom implemation of metric collecotrs called pmda. We wanted to include metrics regarding the databases swift uses for storage. therefor we implemented pmda that is called swiftdbinfo.
The implementaion of the swiftdbinfo pmda is included in the monitoring/pmdas/swiftdbindo directory.
the swiftdbinfo pdam adds 3 additonal metrics for each db in the storage nodes. the swiftdbinfo pdma uses instances to represent the dbs. each of the 3 metrics is associated to the instance domain. resulting in results for each db for each metric.
the metrics are: swiftdbinfo.size, swiftdbinfo.object.count and swiftdbinfo.object.dist (object distrubution).

the swiftdbinfo updates the list of instances (dbs) it tracks by implenting the fetch function. when the function is called by pcp a `find` comand is executed to find all dbs in the file sysytem, then the pdma filters out the only the swift dbs and querries them to extract the container account and hash of the db. the instance name that represtnes the db is in the following format: `{discovery_time}__{container}__{account}__{hash}`.
the discovery time is added to the name of the instnace to allow easy sorting of the instances.
By default swiftdbinfo does not track swift expired objects dbs, this can be changed eaisly by changing the configuration of the pdma. the pdma configuration is located in the beginging of the monitoring/pdmas/swiftdbinfo/pmdaswiftdbinfo.py under `Configuration`. to enable tracking of expired objects set SHOULD_TRACK_EXPIRING_OBJECTS = True.

swiftDBinfo also adds to each db instance a label named `swift_db_name` that is implemted in the simple_label_callback function. the value of the lable is the instnace name. This label is very useful when needing an easy option to get the list of instance names from grafana, by using the biltin functions  that are available for dashboard variables of type Query. in our case the `label_values()` function called with `label_values(swift_db_name)` is used in the the dashboard vairables. for the full list of possible query functions supported by pcp grafana view: https://grafana-pcp.readthedocs.io/en/latest/datasources/redis.html#query-functions

swiftdbinfo.object.dist metric returns the distbution of sizes of objects in the db by returning the number of objects in each size category. the size categories/buckets can be configured in the configuration section of monitoring/pdmas/swiftdbinfo/pmdaswiftdbinfo.py. the deafult buckets are:

0-1 KB, 0-10 KB, 10-100 KB, 100 KB - 1 MB, 1 MB - 10 MB, 10 MB - 25 MB, 25 MB - 50 MB, 50 MB - 100 MB, 100 MB - 500 MB, 500 MB - 1 GB, 1 GB - 5 GB.
(5GB is swift maximum)

the number and sizes of the buckets can be changed depending on the usecase. swiftdbinfo.object.dist metric returns the distrubtuon as a string formated as bucket=number separated by ','. This requires further parsing in the dashboard to represtn the data, this is returned due to pcp data structure as specifed in https://pcp.readthedocs.io/en/latest/PG/WritingPMDA.html#n-dimensional-data.

the swiftdbinfo pdma can be queried directly by running on the relevant storage node:

```
pminfo -f swiftdbinfo
```
The swiftdbinfo logs appear in  cat /var/log/pcp/pmcd/swiftdbinfo.log.

### configuration

As specifed in the previouse section swfitdbinfo pdma supports configuration of:
- number and size of buckets used in swiftdbinfo.object.dist
- the option to enable tracking of expired objects db.

these can be configured by changing constants in monitoring/pdmas/swiftdbinfo/pmdaswiftdbinfo.py in the  `Configuration` comment section.



## built in dashboards

As part of the monitoring process 2 dashboards are added to the grafana instnace. the dashboards are used using the configure_grafana.py python script.
the dashboaords are written in jsonnet using graffonet.the dahboards can be found in monitoring/grafana/dashboards.
the configure_grafan.py generated the json from the jsonnet dashboards and adds them to the grafana instnance.

### host overview

the host overiview dashbaord contains common metrics included in pcp like memory and CPU utilization.
the dashboard is based on pcp host overview dashboard - that can be founf in the pcp grafana repository https://github.com/performancecopilot/grafana-pcp/blob/77809e9996767d0bdc4b88be58ddbf0f273b981d/src/datasources/redis/dashboards/pcp-redis-host-overview.jsonnet.
this dashboard uses an old version of grafonnet, a version that is now deprectaed, and the garph panels it includes are from ttype of graph panel instead of time series that also will benot supported in next versions of grafana. Once pcp creators update to the newer version of gragoonet and update the dahboard it should be updard. the dashboard in additon contains metrics regarding to XFS like  memory consumption by XFS inodes.

### swiftdbinfo

The swiftdbinof dashboard is a dashboard that ocntains the info gather py the swiftdbinfo pdma.
the dashobard vairables contain the option to choose the datasource - from the list of storage nodes.
also the dashobard contains the option to chose the db instances to show. each db instance will have a row in the dashboard that will contain all the metircs of that db. an "All" option is inlcuded that will contain all the dbs in the dashboard.
This dahboard is wriiten with the new updated autoi gnerated version of graffonet.

each row will contain 3 graphs. the object count and db size pannels are regular time series pannels however the object sixe distrubution is a business Charts panel
that is inlcuded as part of the grafana Business Charts plugin. the plugin is installed as part of the moniotring setup. this pannel is formated as an heat map and mostly importatnt contains javascript code that prepares the data to be consumed by the selected visulation. this is very important in casse of pcp complex metrics
that nned additional processing before beeing present, like separaion in to fields for n diminsiol data. This maybe be tried to achived also with built in grafan ttransfomation but th e tranforamtion s did not include enough options, and for full cutomabilty the echart approachd eas taken.

all of the pannels for all of the metics inlcude also grafan transforamtion that filters and shoows only the instnace of the specific row, this is implmentsed with grafna tranforamtion becasue even when querying pcp for a specifc label it returns that results of all of the instnaces therefore the filter is done in grafan level.

# Dashboard customization

A nice feature of the system is the ababilat y to cusomtise the dashboards its possbile to custommize the existing dashboards ot add new ones.

## writing a dashboard jsonnet

dashboards should be implemetn ed with jsonnet, they are the gnerated by the conigute_grafana script and upladed to the grafana.
to add a new dashbaord add it to the monitoring/grafana/dashboards directory. Is recoomernd to use the newest version of grafoonet to write the dashboard
simiilar as can be seen in the swiftdbinfo pdma dashboard. here is alink to the officail docs https://grafana.github.io/grafonnet/index.html. In case additoial
jsonnet libratys ar enneded thay can be added by running in the root of the project:

```
jb install LIBRARY

```
to generate the josn without uplaoding to grafana you can run:

```
jsonnet -J vendor monitoring/grafana/dashboards/dashboard.jsonnet

```

custom dashboards can inlcude addiotnal metrics that are collected by pcp but mot prsented in the dashboards inlcuded in the project. here is  a guide to find all the pcp metrics can be found wit hthe curenmt instalation https://pcp.readthedocs.io/en/latest/QG/ListAvailableMetrics.html.

## steps to include dashboard in deployment

To inlcude the dahboard in the run_with_moniotr script so it is deployed and added to the complete setup add an addiotnal line to the dasboards section in run_with_moniotr script.

```
declare -A dashboards
dashboards["swiftdbinfo.jsonnet"]="swiftdbinfo"
dashboards["pcp-redis-host-overview.jsonnet"]="pcp-host"
ADD HERE (format is: dashboards[file name relative to monitoring/grafana/dashboards dir]=UID of dashobard)

```
the configuratino eincludes specying the uid of the dashobard, the uod of the dashobard will be part of the URI of the dashboard - allowing easy access by URL.
the full URL of the dashbord will be ouputed as part of the script as explained in previous sections.

## buisnees echarts

when implemnting cusotm dashboards it may be a good option to use the buisnes ecaarts pluign. it contians multiple options for additonal visulations adn the option to foramt the data with code that can be very handy when implemtneting cusotm pdmas with data that needs to be parsed beofre visulaized.
link to all visualtions: https://echarts.apache.org/examples/en/index.html#chart-type-line
link to pluign docs https://volkovlabs.io/plugins/business-charts/


# Adding additonal metrics

addiotnal metrics that are collected can be added. pcp gather metrics by a compmment named pdma. It supoort s implemamtion of custom pdmas. before adding new pdmas its good to browse and search for existing pdmas theat can be added to the pcp setup.
But in case of a specif application agenet or not finsin g an exitind agaent and pdma can be implented and easily ingerated.


## implementing a pmda

before impletning a pdma its recommenred to resa the docs regarding the swift dbinfo padm that is also  a custom pamda and can be an example for cusotm pdam wriiten in python.
in addiotn there are a couple of very useful resources to review when implemtitng a new pdma

blog post on a simply python pdma - https://ryandoyle.net/posts/writing-a-pmda-for-pcp/
officcaail programers guide - https://pcp.readthedocs.io/en/latest/PG/WritingPMDA.html
officail pyhtom pdma example - https://github.com/performancecopilot/pcp/blob/main/src/pmdas/simple/pmdasimple.python
directory with all builtin implemted pdmas - can be a good refernce point - https://github.com/performancecopilot/pcp/tree/main/src/pmdas

when adding a new pdma its recommenred to add it to the monitoring/pdmas directory. a directory should be created for each pdma. the directory should include the pdma an the install script as described in the abbove resources.

## adding it to the deployment


once a new pdam is implented its very easy to inlcude its a s part of  the system, all waht nned to be done is add an additional step to the monitor_swift_cluster.yaml playbook


```
- name: Setup PDMA_NAME pmda on storage hosts
  hosts: storage
  tasks:
    - name: Copy pdma to host
      copy:
        src: monitoring/pdmas/PDMA_NAME/
        dest: /var/lib/pcp/pmdas/PDMA_NAME/
        mode: u=rwx,g=rwx,o=rwx
    - name: change ownership pf pdma
      command: sudo chown $USER /var/lib/pcp/pmdas/PDMA_NAME
    - name: Install PDMA
      shell: |
            cd /var/lib/pcp/pmdas/PDMA_NAME
            sudo ./Install
    - name: Enable and configure perssitant logging for custom pdma
      shell: |
            sudo sed -i '/\[access\]/i\
            log mandatory on every INTERVAL seconds {\
            METRIC1_NAME\
            METRIC2_NAME\
            METRIC3_NAME\
            }

            ' /var/lib/pcp/config/pmlogger/config.default
```

Add this step after the "Setup swiftdbinfo pdma on stoargae hosts" step.
when adding the step cahnge alll ocurnces of PDMA_NAME to the name of the pdma.

the last sub step "Enable and configure perssitant logging for custom pdma"
controls the frequency the metrics will be fetched and saved in redis. All metics that are wanted to be included for history querry should be updated in the
pmlogger config. in the step example change INTERVAL to be the desired interval of the logging of the metric and cahnge METRICX_NAME to include the names o fall metrics. for more inf on the structure of the config view https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/7/html/global_file_system_2/s1-loggingperformance#s1-loggingperformance.