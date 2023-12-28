import { Inter } from 'next/font/google'
import styles from '@/styles/Home.module.css'
import { useState } from 'react'
import LoadingButton from '@mui/lab/LoadingButton';
import { TextField } from '@mui/material';
import FileInput from '@/components/FileInput';

const inter = Inter({ subsets: ['latin'] })

interface dataRecord {
  file_name: string
  total: string
  date: string
  seller: string
}

function convertDataRecord(jsonString: string) {
    let obj: dataRecord[] = JSON.parse(jsonString);
    let rows = obj.map(d => <tr key={d.file_name} >  <td>{d.file_name}</td><td>{d.total}</td><td>{d.date}</td><td>{d.seller}</td></tr>);
    return rows;
}

export default function Home() {
  const [pdfFiles, setPdfFiles] = useState<File[]>([]);
  const [answer, setAnswer] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const onFormSubmit = async (e: any) => {
    e.preventDefault();
    if(answer.length){
      setAnswer('')
    }
    setSubmitting(true);

    if (pdfFiles.length === 0) {
      alert('Please upload at least one PDF file.');
      setSubmitting(false);
      return;
    }

    const formData = new FormData();
    pdfFiles.forEach((file) => formData.append('files[]', file));

    try {
      const response = await fetch('/upload_pdfs', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setAnswer(result.answer);
      } else {
        console.log(response)
        setAnswer(`Error: ${response.statusText}`);
      }
    } catch (error: any) {
      setAnswer(`Error: ${error.message}`);
    }

    setSubmitting(false);
  };

  const onFileChange = (e:any) => {
    if (e.target.files) {
        console.log(e.target.files)
        setPdfFiles(Array.from(e.target.files));
    }
  };

  return (
    <>
      <main className={styles.main}>
        <div style={{textAlign: 'center'}}>
          <h1 style={{'paddingBottom': '1rem'}}>Get information on your PDF invoice files.</h1>
          <div className={styles.card}>
            <form onSubmit={onFormSubmit} className={styles.textareaWrapper}>
              <FileInput fileName={pdfFiles[0]?.name ? pdfFiles[0].name : undefined} label="Select a PDF" onChange={onFileChange} acceptedFileTypes=".pdf" />

              <br />

              <br/>
              <LoadingButton
                onClick={onFormSubmit}
                loading={submitting}
                loadingPosition="start"
                variant="contained"
                color="secondary"
              >
                Submit
              </LoadingButton>

            </form>
          </div>

          {!!answer.length &&
            <div className={styles.card}>
                <table>
                  <thead>
                    <th>File Name</th>
                    <th>Total</th>
                    <th>Date</th>
                    <th>Seller</th>
                  </thead>
                  <tbody>
                     {convertDataRecord(answer)}
                  </tbody>
                </table>
            </div>
          }
        </div>
      </main>
    </>
  )
}
