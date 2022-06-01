#include "mainwindow.h"
#include "ui_mainwindow.h"
#include <QFileDialog>
#include <QStringList>
#include <QLabel>
#include <QMovie>
#include <QDebug>
#include <QString>
#include <QTextBrowser>
#include <QMessageBox>
#include <QByteArray>
#include <stdio.h>
#include <iostream>
#include <string.h>
#include <windows.h>
#include <QtMultimedia/QMediaPlayer>
#include <QTimer>
#include <fstream>
#include <string>

std::string mycmd;
FILE *fp;

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    std::ifstream inFile("./config.txt",std::ios::in);
    std::getline(inFile, mycmd);
    inFile.close();

    ui->setupUi(this);
    ui->pushButton->setFont(QFont("Algerian",20));
    ui->pushButton->setStyleSheet("QPushButton{background: transparent; color:orange; }""QPushButton:hover{color:red;}");

    ui->pushButton_2->setFont(QFont("Algerian",20));
    ui->pushButton_2->setStyleSheet("QPushButton{background: transparent; color:orange; }""QPushButton:hover{color:red;}");
    // CHANGE
    ui->pushButton_3->setFont(QFont("Algerian",25));
    ui->pushButton_3->setStyleSheet("QPushButton{background: transparent; color:white; }""QPushButton:hover{color:red;}");
    ui->pushButton_4->setFont(QFont("Algerian",10));
    ui->pushButton_4->setStyleSheet("QPushButton{background: transparent; color:orange; }""QPushButton:hover{color:red;}");

    ui->pushButton_5->setFont(QFont("Algerian",10));
    ui->pushButton_5->setStyleSheet("QPushButton{background: transparent; color:orange; }""QPushButton:hover{color:red;}");

    ui->pushButton_6->setFont(QFont("Algerian",10));
    ui->pushButton_6->setStyleSheet("QPushButton{background: transparent; color:orange; }""QPushButton:hover{color:red;}");
    ui->pushButton_7->setFont(QFont("Algerian",20));
    ui->pushButton_7->setStyleSheet("QPushButton{background: transparent; color:orange; }""QPushButton:hover{color:red;}");

    ui->pushButton_8->setFont(QFont("Algerian",10));
    ui->pushButton_8->setStyleSheet("QPushButton{background: transparent; color:orange; }""QPushButton:hover{color:red;}");

    ui->textBrowser->setWindowFlags(Qt::FramelessWindowHint);

    QLabel *label = new QLabel(this);
    movie = new QMovie("F:/QTproject/test/mmm.GIF");
    label->setMovie(movie);
    movie->start();
    movie->stop();
    label->show();
    label->setScaledContents(true);
    label->setGeometry(220,160,210,210);

    /* Thread */
    mythread = new Thread;
    connect(mythread, &Thread::stopPlaying, this, [=](){
        movie->stop();
    });
    connect(mythread,&Thread::finished,this,&run_cmd);

    setWindowFlags(windowFlags() | Qt::WindowStaysOnTopHint);
    setAttribute(Qt::WA_TranslucentBackground);
    showNormal();


    src_flag = false;
    dst_flag = false;
    res_flag = false;
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::read_file(int pos){
    QStringList filenames = QFileDialog::getOpenFileNames(this,tr("请选择待转换声音文件"), "./:", tr("声音文件(*wav *mp3);"));
    qDebug()<< "fileNames:" << filenames;
    if(filenames.size() == 0) return;
    QString file = filenames[0];
    QString filename = file.mid(file.lastIndexOf('/')+1);
    QByteArray ba = file.toLatin1();
    if(pos == 1){
       ui->label->setText(filename);
       src = file;
       src_flag = true;
    }
    else if(pos == 2){
       ui->label_2->setText(filename);
       dst = file;
       dst_flag = true;
    }
    else if(pos == 3){
       ui->label_3->setText(filename);
       res = file;
       res_flag = true;
    }
}

int MainWindow::run_cmd(){
    std::string buf;
    std::ifstream inFile("./output.txt",std::ios::in);

    while(std::getline(inFile,buf)){
        //ui->textBrowser->insertPlainText(QString(buf));
        //ui->textBrowser->insertHtml(QString("<font color=white>")+QString::fromLocal8Bit(buf)+QString("</font><br"));
        ui->textBrowser->setTextColor(QColor("white"));
        QString content = QString::fromLocal8Bit(buf.c_str());
        // qDebug() << content;
        ui->textBrowser->insertPlainText(content);
        ui->textBrowser->moveCursor(QTextCursor::End);
        ui->textBrowser->append(QString(""));
    }

    inFile.close();
}

void MainWindow::play_sound(const QString &file){
    QMediaPlayer *player = new QMediaPlayer;
    player->setMedia(QUrl::fromLocalFile(file));
    player->setVolume(70);
    player->play();
}

void MainWindow::on_pushButton_clicked()
{
    read_file(1);
}

void MainWindow::on_pushButton_2_clicked()
{
    read_file(2);
}

void MainWindow::on_pushButton_3_clicked()
{
    movie->start();
    mythread->start();
    showNormal();
}

void MainWindow::on_pushButton_4_clicked()
{
   ui->textBrowser->setText("");
}

void MainWindow::on_pushButton_5_clicked()
{
    if(src_flag)
        play_sound(src);
}

void MainWindow::on_pushButton_6_clicked()
{
    if(dst_flag)
        play_sound(dst);
}

void MainWindow::on_pushButton_7_clicked()
{
    read_file(3);

}

void MainWindow::on_pushButton_8_clicked()
{
    if(res_flag)
        play_sound(res);
}


Thread::Thread()
{

}

void Thread::run(){
    fp = _popen(mycmd.c_str(), "r");
    char buf[1000];
    memset(buf, 0, sizeof(buf));
    std::ofstream outFile("./output.txt",std::ios::out);
    while (fgets(buf, sizeof(buf), fp)){
        qDebug() << QString::fromLocal8Bit(buf);
        outFile.write(buf,strlen(buf));
    }
    outFile.close();
    emit stopPlaying();
    qDebug()<<"end";
}
