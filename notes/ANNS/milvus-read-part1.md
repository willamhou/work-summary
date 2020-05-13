## milvus-read : part1

 milvus源码解析以0.8.0版本为基准.

 整个服务的入口流程在main.cpp中.

 在main.cpp中主要是两步

* 获取server实例
* server参数初始化和start

~~~C++
/* 获取server实例~~~ server是个单例类 */
milvus::server::Server& server = milvus::server::Server::GetInstance();

/* 
server初始化
server启动
其中Init函数的入参都是在后台启动时候传入的参数
*/
server.Init(start_daemonized, pid_filename, config_filename, log_config_file);

s = server.Start();
if (s.ok()) {
    std::cout << "Milvus server started successfully!" << std::endl;
} else {
    std::cout << s.message() << std::endl;
    goto FAIL;
}
~~~



在server.cpp中最重要的是Init和Start函数.

~~~C++
/* 函数实现很简单, 主要是将配置参数赋值给server内部成员变量 */
void Server::Init(int64_t daemonized, const std::string& pid_filename, const std::string& config_filename,
             const std::string& log_config_file) {
    daemonized_ = daemonized;
    pid_filename_ = pid_filename;
    config_filename_ = config_filename;
    log_config_file_ = log_config_file;
}
~~~

~~~C++
/*
  start函数里主要完成了以下功能
  1. config的参数解析
  2. 判断是单机还是集群
  3. 判断是CPU还是GPU模式, 并对其环境配置进行检查
  4. 通过调用StartService函数完成服务的启动
*/

Status Server::Start() {
    if (daemonized_ != 0) {
        Daemonize();
    }

    try {
        /* Read config file */
        Status s = LoadConfig();
        if (!s.ok()) {
            std::cerr << "ERROR: Milvus server fail to load config file" << std::endl;
            return s;
        }

        Config& config = Config::GetInstance();

        /* Init opentracing tracer from config */
        std::string tracing_config_path;
        s = config.GetTracingConfigJsonConfigPath(tracing_config_path);
        tracing_config_path.empty() ? tracing::TracerUtil::InitGlobal()
                                    : tracing::TracerUtil::InitGlobal(tracing_config_path);

        /* log path is defined in Config file, so InitLog must be called after LoadConfig */
        std::string time_zone;
        s = config.GetServerConfigTimeZone(time_zone);
        if (!s.ok()) {
            std::cerr << "Fail to get server config timezone" << std::endl;
            return s;
        }

        if (time_zone.length() == 3) {
            time_zone = "CUT";
        } else {
            int time_bias = std::stoi(time_zone.substr(3, std::string::npos));
            if (time_bias == 0) {
                time_zone = "CUT";
            } else if (time_bias > 0) {
                time_zone = "CUT" + std::to_string(-time_bias);
            } else {
                time_zone = "CUT+" + std::to_string(-time_bias);
            }
        }

        if (setenv("TZ", time_zone.c_str(), 1) != 0) {
            return Status(SERVER_UNEXPECTED_ERROR, "Fail to setenv");
        }
        tzset();

        {
            bool trace_enable = false;
            bool debug_enable = false;
            bool info_enable = false;
            bool warning_enable = false;
            bool error_enable = false;
            bool fatal_enable = false;
            std::string logs_path;
            int64_t max_log_file_size = 0;
            int64_t delete_exceeds = 0;
            s = config.GetLogsTraceEnable(trace_enable);
            if (!s.ok()) {
                return s;
            }
            s = config.GetLogsDebugEnable(debug_enable);
            if (!s.ok()) {
                return s;
            }
            s = config.GetLogsInfoEnable(info_enable);
            if (!s.ok()) {
                return s;
            }
            s = config.GetLogsWarningEnable(warning_enable);
            if (!s.ok()) {
                return s;
            }
            s = config.GetLogsErrorEnable(error_enable);
            if (!s.ok()) {
                return s;
            }
            s = config.GetLogsFatalEnable(fatal_enable);
            if (!s.ok()) {
                return s;
            }
            s = config.GetLogsPath(logs_path);
            if (!s.ok()) {
                return s;
            }
            s = config.GetLogsMaxLogFileSize(max_log_file_size);
            if (!s.ok()) {
                return s;
            }
            s = config.GetLogsDeleteExceeds(delete_exceeds);
            if (!s.ok()) {
                return s;
            }
            InitLog(trace_enable, debug_enable, info_enable, warning_enable, error_enable, fatal_enable, logs_path,
                    max_log_file_size, delete_exceeds);
        }

        std::string deploy_mode;
        s = config.GetServerConfigDeployMode(deploy_mode);
        if (!s.ok()) {
            return s;
        }

        if (deploy_mode == "single" || deploy_mode == "cluster_writable") {
            std::string db_path;
            s = config.GetStorageConfigPrimaryPath(db_path);
            if (!s.ok()) {
                return s;
            }

            try {
                // True if a new directory was created, otherwise false.
                boost::filesystem::create_directories(db_path);
            } catch (...) {
                return Status(SERVER_UNEXPECTED_ERROR, "Cannot create db directory");
            }

            s = InstanceLockCheck::Check(db_path);
            if (!s.ok()) {
                std::cerr << "deploy_mode: " << deploy_mode << " instance lock db path failed." << std::endl;
                return s;
            }

            bool wal_enable = false;
            s = config.GetWalConfigEnable(wal_enable);
            if (!s.ok()) {
                return s;
            }

            if (wal_enable) {
                std::string wal_path;
                s = config.GetWalConfigWalPath(wal_path);
                if (!s.ok()) {
                    return s;
                }

                try {
                    // True if a new directory was created, otherwise false.
                    boost::filesystem::create_directories(wal_path);
                } catch (...) {
                    return Status(SERVER_UNEXPECTED_ERROR, "Cannot create wal directory");
                }
                s = InstanceLockCheck::Check(wal_path);
                if (!s.ok()) {
                    std::cerr << "deploy_mode: " << deploy_mode << " instance lock wal path failed." << std::endl;
                    return s;
                }
            }
        }

        // print version information
        LOG_SERVER_INFO_ << "Milvus " << BUILD_TYPE << " version: v" << MILVUS_VERSION << ", built at " << BUILD_TIME;
#ifdef MILVUS_GPU_VERSION
        LOG_SERVER_INFO_ << "GPU edition";
#else
        LOG_SERVER_INFO_ << "CPU edition";
#endif
        s = StorageChecker::CheckStoragePermission();
        if (!s.ok()) {
            return s;
        }

        s = CpuChecker::CheckCpuInstructionSet();
        if (!s.ok()) {
            return s;
        }

#ifdef MILVUS_GPU_VERSION
        s = GpuChecker::CheckGpuEnvironment();
        if (!s.ok()) {
            return s;
        }
#endif
        /* record config and hardware information into log */
        LogConfigInFile(config_filename_);
        LogCpuInfo();
        LogConfigInMem();

        server::Metrics::GetInstance().Init();
        server::SystemInfo::GetInstance().Init();

        return StartService();
    } catch (std::exception& ex) {
        std::string str = "Milvus server encounter exception: " + std::string(ex.what());
        return Status(SERVER_UNEXPECTED_ERROR, str);
    }
}


~~~





~~~C++
/*
   StartService是Server服务实际启动的地方, 主要涉及以下几个地方
   1.KnowhereResource的初始化, 这部分主要涉及的是GPU的资源管理和搜索
   2.scheduler的初始化和启动, 这部分涉及了各个task的调度
   3.GrpcServer的初始化和启动, 这部分是在线服务的实际处理方
   4.WebServer的初始化和启动, 这部分是web部分的实际处理方
*/

Status Server::StartService() {
    Status stat;
    stat = engine::KnowhereResource::Initialize();
    if (!stat.ok()) {
        LOG_SERVER_ERROR_ << "KnowhereResource initialize fail: " << stat.message();
        goto FAIL;
    }

    scheduler::StartSchedulerService();

    stat = DBWrapper::GetInstance().StartService();
    if (!stat.ok()) {
        LOG_SERVER_ERROR_ << "DBWrapper start service fail: " << stat.message();
        goto FAIL;
    }

    grpc::GrpcServer::GetInstance().Start();
    web::WebServer::GetInstance().Start();

    // stat = storage::S3ClientWrapper::GetInstance().StartService();
    // if (!stat.ok()) {
    //     LOG_SERVER_ERROR_ << "S3Client start service fail: " << stat.message();
    //     goto FAIL;
    // }

    //    search::TaskInst::GetInstance().Start();

    return Status::OK();
FAIL:
    std::cerr << "Milvus initializes fail: " << stat.message() << std::endl;
    return stat;
}

~~~

