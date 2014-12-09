/* Kruskal算法求最小生成树,无向图使用邻接矩阵表示 */

#include "Stdio.h"
#include "Conio.h"

#define MaxNum 50          /*图的最大顶点数为50*/
#define MaxEdge 2500       /*图中的最大边数*/
#define MAX 32767          /*表示计算机中最大整数,假设为边上权值不能取的无穷大*/

typedef char VexType[3];        /*图的顶点类型设为字符数组，2个字符长度*/
typedef int EdgeType;           /*弧（边）的权值设为整型*/
typedef struct {
    VexType V[MaxNum];          /*一维数组存储顶点信息*/
    EdgeType E[MaxNum][MaxNum]; /*二维数组表示邻接矩阵，存储边的信息*/
    int n,e;                    /*顶点数和边数*/
}MGraph;                        /*图类型定义*/

int Locate(MGraph *G,char vex[])  /*确定顶点在图G中的位置，即在G->V中的序号*/
{
int i;
for(i=0;i<G->n;i++)
if(strcmp(G->V[i],vex)==0)
return i;
}

void CreateGraph(MGraph *G)
      {
       int i,j,k,cost;
       char vex1[3],vex2[3];/*保存输入的顶点*/
       printf("\n输入图的顶点数和边数(用逗号分隔):");
       scanf("%d,%d",&(G->n),&(G->e));/*输入顶点数和边数*/
       printf("输入图的顶点信息(最长2个字符):");
for (i=0;i<G->n;i++)
{
 /*G->V[i][0]=G->V[i][1]=0;*/
 scanf("\n%s",G->V[i]); /*输入n个顶点的标识信息，建立顶点数组*/
}
       for (i=0;i<G->n;i++)
   for (j=0;j<G->n;j++)  
G->E[i][j]=MAX;  /*对邻接矩阵元素进行初始化*/
       printf("\n输入图中每条边所依附的两个顶点的标识信息:");
       for (k=0;k<G->e;k++)         /*输入e条边*/
        {
        printf("\n输入第%d条边的第1个顶点：",k+1);
        scanf("%s",vex1);
        printf("输入第%d条边的第2个顶点：",k+1);
        scanf("%s",vex2);
        /* scanf("%s\n%s",vex1,vex2);*/
        i=Locate(G,vex1);j=Locate(G,vex2);
   /*     scanf("\n%d,%d",&i,&j); */   /*输入每条边所依附的顶点在二维数组中的下标，建立邻接矩阵*/
        printf("\n输入第%d条边的权值：",k+1);
        scanf("%d",&cost);
         G->E[i][j]=cost;             /*如果同时输入G->E[j][i]=cost;，则是建立无向图的邻接矩阵*/
        }
}

void PrintGraph(MGraph *G)/*打印图的顶点和边的信息*/
{
int i,j;
printf("\n图中顶点个数为：%d",G->n);
printf("\n图中边数为：%d",G->e);
printf("\n图中顶点为：");
for (i=0;i<G->n;i++)
printf("%c%c ",G->V[i][0],G->V[i][1]);
printf("\n图中边为：");
for(i=0;i<G->n;i++)
   for(j=0;j<G->n;j++)
    if(G->E[i][j])
        printf("[%c%c,%c%c] ",G->V[i][0], G->V[i][1], G->V[j][0], G->V[j][1]);
}

/*将图中边的信息保存在一维数组edges中*/
typedef struct{       /*数组元素类型定义*/
    char elem1[3];    /*边所依附的第一个顶点*/
    char elem2[3];    /*边所依附的第二个顶点*/
    int cost;         /*保存权值*/
   }EdgeType;
EdgeType edges[MaxEdge];

void CreateEdge(MGraph *G,EdgeType edges[])/*将边信息保存到一维数组中*/
{
int i,j;
int k=0;
for(i=0;i<G->n;i++)
   for(j=0;j<G->n;j++)
   if(G->E[i][j]!=MAX)
   {
    strcpy(edges[k].elem1,G->V[i]);
    strcpy(edges[k].elem2,G->V[j]);
    edges[k].cost=G->E[i][j];
    k=k+1;
   }
}

void SortEdge(EdgeType edges[],int n)/*将一维数组的元素按照cost由小到大进行冒泡排序*/
{                                    /*n是边数*/
int i,j;
EdgeType temp;
for (i=n；i>1；i--）
{
    for (j=0;j<i-1;j++)
    if（edges[j].cost>edges[j+1].cost）
    {

      strcpy(temp.elem1,edges[j].elem1);
      strcpy(temp.elem2,edges[j].elem2);
      temp.cost=edges[j].cost;
      strcpy(edges[j].elem1,edges[j+1].elem1);
      strcpy(edges[j].elem2,edges[j+1].elem2);
      edges[j].cost=edges[j+1].cost;
      strcpy(edges[j+1].elem1,temp.elem1);
      strcpy(edges[j+1].elem2,temp.elem2);
      edges[j+1].cost=temp.cost;
    }
}
}

int Find（int father[ ]，int v）
 /*寻找顶点v所在树的根结点*/
 { int t;
      t=v;
  while(father[t]>=0)
    t=father[t];
  return(t);
 }

void Kruskal（EdgeType edges[ ]，int n）
 /*用Kruskal方法构造有n个顶点的图edges的最小生成树*/
 {
  int father[MaxNum];
  int i,j,vf1,vf2;
  for (i=0;i<n;i++) father[i]=-1;
  i=0;j=0;
  while(i<MaxEdge && j<n-1)
    { vf1=Find(father,edges[i].elem1);
      vf2=Find(father,edges[i].elem2);
      if (vf1!=vf2)
       { father[vf2]=vf1;
         j++;  /*j表示当前最小生成树的顶点个数*/
         printf("%3d%3d\n",edges[i].v1,edges[i].v2);
       }
      i++;
    }
}


main()
{
 /* 此处添加你自己的代码 */
getch();
}
