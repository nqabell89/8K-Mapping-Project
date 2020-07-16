LOGFILE = format(Sys.time(), "%b_%d_%Y.log")
print(LOGFILE)

DF_FILTER_LIST <- data.frame(
  start_text = c('Introduction',
                 'FUNCTIONAL EARNINGS', 
                 'DISCUSSION AND ANALYSIS',
                 'DISCUSSION AND ANALYSIS',
                 'DISCUSSION AND ANALYSIS',
                 'OVERVIEW',
                 'Business Overview',
                 'Financial Review',
                 'RESULTS OF OPERATIONS',
                 'Overview',
                 'Entergy operates',
                 "MANAGEMENT\'S FINANCIAL DISCUSSION",
                 'General',
                 "Management's Discussion",
                 'EXECUTIVE SUMMARY',
                 'EXECUTIVE OVERVIEW',
                 'EXECUTIVE OVERVIEW',
                 'The following management discussion and analysis',
                 'CURRENT ECONOMIC CONDITIONS',
                 'Overview and Highlights',
                 'Financial Review - Results of Operations'),
  end_text = c('Quantitative and qualitative disclosures about market risk',
               "MANAGEMENT\'S REPORT",
               'RISK FACTORS',
               'FIVE-YEAR PERFORMANCE GRAPH',
               'FINANCIAL STATEMENTS AND NOTES',
               'Risk management includes the identification',
               'Selected Loan Maturity Data',
               'Risk Management',
               'QUANTITATIVE AND QUALITATIVE DISCLOSURES',
               'Forward-Looking Statements',
               'New Accounting Pronouncements',
               'New Accounting Pronouncements',
               'Website information',
               'Risk Disclosures',
               'RISK FACTORS',
               'A summary of contractual obligations is included',
               'CONSOLIDATED RESULTS OF OPERATIONS',
               'NON-GAAP FINANCIAL MEASURES',
               'FORWARD-LOOKING STATEMENTS',
               'Critical Accounting Policies and Estimates',
               'Unregistered Sales of Equity Securities and Use of Proceeds')
)


CSVFILE = format(Sys.time(), "%b_%d_%Y.csv")
CSVFILE = format(Sys.time(), "file_index.csv")
print(CSVFILE)

get_filings_links <-function(str_ticker) {
  df_filings <- company_filings(str_ticker, type = "10-", count = 20)
  df_filings <- df_filings[df_filings$type == "10-K" | df_filings$type == "10-Q", ]
  df_filing_infos <- map_df(df_filings$href, filing_information)
  df_filings <- bind_cols(df_filings, df_filing_infos)
  return(head(as_tibble(df_filings),20))
}

write_log <- function(str_text) {
  print(str_text)
  if (file.exists(LOGFILE)) {
    write(str_text,file=LOGFILE,append=TRUE)
  } else {
    write(str_text,file=LOGFILE,append=FALSE)
  }
}

write_log_csv <- function(df) {
  if (file.exists(CSVFILE)) {
    write_csv(df,CSVFILE,append=TRUE)
  } else {
    write_csv(df,CSVFILE,append=FALSE)
  }
}

get_mdna_text <- function(str_ticker) {
  #str_ticker <- 'AXP'
  
  df_filing_documents <- read_csv('file_index.csv') %>%
    #select(document,href,type...7,ticker) %>%
    filter(ticker == str_ticker)

  str_section = 'item 2|item 7'
  str_search = 'discussion'
  
  df_filing_documents <- df_filing_documents[df_filing_documents$type...7 == "10-K" | df_filing_documents$type...7 == "10-Q",]
  
  #a_row = 1
  for (a_row in 1:nrow(df_filing_documents)) {
    #df_filing_documents[a_row,'href']
    str_doc_href <- df_filing_documents[a_row, "href"]
    file_end <- gsub("https://www.sec.gov",'',str_doc_href)
    file_name = paste0(getwd(),file_end)
    file_name = gsub('.htm','.csv',file_name)
    
    result <- try({
      df_docs <- read_csv(file_name)
    }, silent = TRUE)
    
    if ( "try-error" %in% class(result) ) {
      err_msg <- geterrmessage()
      print(err_msg)
      next
    }
    
    file_doc <- df_docs[df_docs$type == "10-K" | df_docs$type == "10-Q",]$href
    file_doc <- gsub("https://www.sec.gov",'',file_doc)
    file_doc <- paste0(getwd(),'/',file_doc)
    file_doc <- gsub('.htm','.csv',file_doc)
    
    result <- try({
      doc <- read_csv(file_doc,col_types = cols(.default = "c"))
    }, silent = TRUE)
    
    if ( "try-error" %in% class(result) ) {
      err_msg <- geterrmessage()
      print(err_msg)
      next
    }
    
    df_txt <- doc[grepl(str_section, doc$item.name, ignore.case = TRUE) & grepl(str_search, doc$item.name, ignore.case = TRUE), ] # only discussion for now
    
    i_start = ''
    i_end = ''
    
    if (nrow(df_txt) ==0) {
    #b_row = 1
    for (b_row in 1:nrow(DF_FILTER_LIST)) { #should flip this to apply()
      
        start_text <- DF_FILTER_LIST[b_row, "start_text"]
        end_text <- DF_FILTER_LIST[b_row, "end_text"]
      
        write_log(paste0('trying ',start_text))
        write_log(paste0('to ',end_text))
      
        i_start = as.integer(which(grepl(start_text, doc$text))) 
        if (length(i_start) > 1) { #handle table of contents duplicates
          i_start = i_start[2]
        }
        i_end = as.integer(which(grepl(end_text, doc$text)))
        if (length(i_end) > 1) {
          i_end = i_end[2]
        }
      
        write_log(i_start)
        write_log(i_end)
      
        if (length(i_start) != 0 & length(i_end) != 0) {
          if (i_start < i_end) {        
            print(paste0('istart is:',i_start,' iend is:',i_end))
            df_txt = doc[i_start:i_end,]
            break
          }
        }
      } 
    }
    
    if (length(i_start) == 0 || length(i_end) == 0) {
        write_log("missing section for:")
        write_log(str_href)
    }
    
    mdna_file_name <- gsub('.csv','_mdna.csv',file_doc)
    df_txt <- as_tibble(df_txt) %>%
      mutate(section = str_search) %>%
      write_csv(mdna_file_name)
    }
  
}

get_ticker_text <- function(str_ticker, force = FALSE) { #not using force yet
  # get the full text of filing and save as a csv
  start_time <- Sys.time()
  
  write_log(str_ticker)
  
  str_write_name <- paste0('sec_data_folder/',str_ticker)
  
  write_log("get filings links ...")
  
  filings_csv <- paste0(str_write_name,"_filings.csv")
  
  #if (file.exists(filings_csv)) {  
  #  write_log("from cache ...")
  #  
  #  df_filings <- read_csv(filings_csv,col_types = cols()) 
  #  df_filings <- df_filings %>% mutate_if(is.logical, as.character)
  #} else {
  write_log("from sec ...")
    
  df_filings <- get_filings_links(str_ticker) %>%
      mutate(ticker = str_ticker) %>%
      write_csv(filings_csv)
  #}
  
  write_log_csv(df_filings)

  df_filings %>%
    rowwise() %>%
    mutate(nest_discussion = map(.x = href, .f = get_documents_text))
  
  end_time <- Sys.time()
  write_log(end_time - start_time)
  
}

get_string_file_name <- function(str_href) {
  #str_href <- 'https://www.sec.gov/Archives/edgar/data/4962/000000496220000054/0000004962-20-000054-index.htm'
  str_file_path <- ''
  file_path = strsplit(str_href,'/')
  for (i in 5:length(file_path[[1]])-1) {
    str_file_path = paste0(str_file_path,"/",(file_path[[1]][i]))
  }
  str_file_path <- paste0(getwd(),"/",str_file_path)
  dir.create(str_file_path,recursive = TRUE)
  str_file_path
  str_file_name <- ''
  file_path = strsplit(str_href,'/')
  for (i in 4:length(file_path[[1]])) {
    str_file_name = paste0(str_file_name,"/",(file_path[[1]][i]))
  }
  str_file_name <- paste0(getwd(),str_file_name)
  str_file_name <- gsub(".htm",".csv",str_file_name)
  return(str_file_name)
}

get_documents_text <- function(str_href) {
  write_log("next link:")
  write_log(str_href)
  #str_href <- 'https://www.sec.gov/Archives/edgar/data/4962/000000496219000018/0000004962-19-000018-index.htm'
  str_file_name <- get_string_file_name(str_href)

  write_log("get filing documents from sec ...")
    
  df_filing_documents <- filing_documents(str_href) %>%
          filter(!grepl('.pdf',str_href)) %>%
          write_csv(str_file_name)

  str_doc_href <- df_filing_documents[df_filing_documents$type == "10-K" | df_filing_documents$type == "10-Q",]$href
  doc <- parse_filing(str_doc_href)    
  
  file_end <- gsub("https://www.sec.gov",'',str_doc_href)
  file_name = paste0(getwd(),file_end)
  str_file_path <- ''
  file_path = strsplit(file_name,'/')
  for (i in 3:length(file_path[[1]])-1) {
      str_file_path = paste0(str_file_path,"/",(file_path[[1]][i]))
  }
  str_file_path <- paste0(str_file_path,"/")
  dir.create(str_file_path,recursive = TRUE)
  file_name = gsub('.htm','.csv',file_name)
  write_csv(as_tibble(doc),file_name)
  print(file_name)
    
  #}
}



#write_log("get section text ...")

#df_data <- (df_filings) %>%
#  rowwise() %>%
#  mutate(nest_discussion = map(.x = href, .f = get_mdna_text)) %>%
#  ungroup() %>%
#  group_by(period_date) %>%
#  arrange(desc(period_date))

#jenky - find a rowwise application
#a <- df_data %>%
#  select(period_date,filing_date,type,form_name,documents,nest_discussion) %>%
#  unnest(nest_discussion)

#write_log("write to local csv  ...")
#df_data <- a %>%
#  as_tibble() %>%
#  write_csv(paste0(str_write_name,".csv"))
