#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QString>
#include <QThread>
#include <QMovie>

const int MAXFILEPATHLENGTH = 100;

namespace Ui {
class MainWindow;
}

class Thread:public QThread
{
    Q_OBJECT
public:
    Thread();
    void run();
signals:
    void stopPlaying();
};

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    friend class Thread;
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();
    QMovie *movie;
    Thread *mythread;
private slots:

    void on_pushButton_clicked();

    void on_pushButton_2_clicked();

    void on_pushButton_3_clicked();

    void on_pushButton_4_clicked();

    void on_pushButton_5_clicked();

    void on_pushButton_6_clicked();

    void on_pushButton_7_clicked();

    int run_cmd();

    void on_pushButton_8_clicked();

private:
    void read_file(int pos);
    void play_sound(const QString &file);
    Ui::MainWindow *ui;
    QString src, dst, res;
    bool src_flag, dst_flag, res_flag;
};

#endif // MAINWINDOW_H
