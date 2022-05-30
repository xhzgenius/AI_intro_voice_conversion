#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QString>

const int MAXFILEPATHLENGTH = 100;

namespace Ui {
class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();

private slots:
    void on_pushButton_clicked();

    void on_pushButton_2_clicked();

    void on_pushButton_3_clicked();

    void on_pushButton_4_clicked();

    void on_pushButton_5_clicked();

    void on_pushButton_6_clicked();

    void on_pushButton_7_clicked();

private:
    void read_file(int pos);
    void play_sound(const QString &file);
    int run_cmd(const char *cmd = NULL);
    Ui::MainWindow *ui;
    QString src, dst, res;
    bool src_flag, dst_flag, res_flag;
};

#endif // MAINWINDOW_H
