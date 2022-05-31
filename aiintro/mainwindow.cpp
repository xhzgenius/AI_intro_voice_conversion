#include "mainwindow.h"
#include "ui_mainwindow.h"
#include <QFileDialog>
#include <QStringList>
#include <QDebug>
#include <QString>
#include <QTextBrowser>
#include <QMessageBox>
#include <QByteArray>
#include <stdio.h>
#include <string.h>
#include <QtMultimedia/QMediaPlayer>

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    ui->pushButton->setFont(QFont("Algerian",20));
    ui->pushButton->setStyleSheet("QPushButton{background: transparent; color:black; }""QPushButton:hover{color:red;}");
    ui->pushButton_2->setFont(QFont("Algerian",20));
    ui->pushButton_2->setStyleSheet("QPushButton{background: transparent; color:black; }""QPushButton:hover{color:red;}");
    ui->pushButton_3->setFont(QFont("Algerian",30));
    ui->pushButton_3->setStyleSheet("QPushButton{background: transparent; color:black; }""QPushButton:hover{color:red;}");
    ui->pushButton_4->setFont(QFont("Algerian",10));
    ui->pushButton_4->setStyleSheet("QPushButton{background: transparent; color:black; }""QPushButton:hover{color:red;}");
    ui->pushButton_5->setFont(QFont("Algerian",10));
    ui->pushButton_5->setStyleSheet("QPushButton{background: transparent; color:black; }""QPushButton:hover{color:red;}");
    ui->pushButton_6->setFont(QFont("Algerian",10));
    ui->pushButton_6->setStyleSheet("QPushButton{background: transparent; color:black; }""QPushButton:hover{color:red;}");
    ui->pushButton_7->setFont(QFont("Algerian",30));
    ui->pushButton_7->setStyleSheet("QPushButton{background: transparent; color:black; }""QPushButton:hover{color:red;}");

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
    QString filename = file.mid(file.lastIndexOf('/')+1)+"已装填！";
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
}

int MainWindow::run_cmd(const char *cmd){
    if(!cmd) return -1;
    char buf[1000];
    FILE *fp;
    if ((fp = _popen(cmd, "r")) == NULL) return -2;
    else{
        memset(buf, 0, sizeof(buf));
        while (fgets(buf, sizeof(buf), fp)){
          qDebug() << buf;
          ui->textBrowser->insertPlainText(QString(buf));
          ui->textBrowser->moveCursor(QTextCursor::End);
          ui->textBrowser->append(QString(""));
        }
        if(_pclose(fp) == -1) return -3;
    }
    return 0;
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
    run_cmd("python test.py");
}

void MainWindow::on_pushButton_4_clicked()
{
    int result = QMessageBox::question(this,"WARNING","真的要把所有信息清空吗？", QMessageBox::Yes|QMessageBox::No, QMessageBox::NoButton);
    if(result == QMessageBox::Yes)
        ui->textBrowser->setText("");
}

void MainWindow::on_pushButton_5_clicked()
{
    if(src_flag)
        play_sound(src);
    else
        QMessageBox::warning(this, "WARNING", "请先选择WAV声音文件");
}

void MainWindow::on_pushButton_6_clicked()
{
    if(dst_flag)
        play_sound(dst);
    else
        QMessageBox::warning(this, "WARNING", "请先选择WAV声音文件");
}

void MainWindow::on_pushButton_7_clicked()
{
    if(res_flag)
        play_sound(res);
    else
        QMessageBox::warning(this, "WARNING", "请先进行转换");
}
